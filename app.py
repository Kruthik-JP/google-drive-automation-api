from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Query
from pydantic import BaseModel
from typing import Optional, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import os
import io
import base64
import tempfile

app = FastAPI(title="Google Drive API Optimized")

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file"
]


# ==============================
# MODELS
# ==============================
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]

# ==============================
# UTILS
# ==============================
def build_service_from_token(access_token: str):
    """Build Google Drive service from access token"""
    try:
        creds = Credentials(token=access_token, scopes=SCOPES)
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid access token: {e}")

def build_file_path(service, file_id: str) -> str:
    """Recursively build full path of a file"""
    try:
        file = service.files().get(fileId=file_id, fields="id, name, parents").execute()
        name = file["name"]
        parents = file.get("parents", [])
        path_parts = [name]

        while parents:
            parent_id = parents[0]
            parent = service.files().get(fileId=parent_id, fields="id, name, parents").execute()
            path_parts.insert(0, parent["name"])
            parents = parent.get("parents", [])

        return "/".join(path_parts)
    except Exception as e:
        return f"Error building path: {e}"

def get_file_as_base64(service, file_id: str) -> str:
    """Download a file and return Base64 encoded string"""
    try:
        request = service.files().get_media(fileId=file_id)
        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        file_data.seek(0)
        return base64.b64encode(file_data.read()).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {e}")

def extract_token(authorization: Optional[str], access_token: Optional[str]) -> str:
    """Get token from header or query param and remove 'Bearer ' if present"""
    token = authorization or access_token
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")
    return token.replace("Bearer ", "").strip()

# ==============================
# ROUTES
# ==============================
@app.post("/google/auth", response_model=AuthResponse)
async def google_auth(file: UploadFile = File(...)):
    """
    Upload credentials.json, perform OAuth, and return access and refresh tokens.
    Only JSON files are accepted.
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JSON credentials file.")

    try:
        tmp_file = os.path.join(tempfile.gettempdir(), "credentials.json")
        with open(tmp_file, "wb") as f:
            f.write(await file.read())

        flow = InstalledAppFlow.from_client_secrets_file(tmp_file, SCOPES)
        creds = flow.run_local_server(port=0)

        return AuthResponse(
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            token_uri=creds.token_uri,
            client_id=creds.client_id,
            client_secret=creds.client_secret,
            scopes=creds.scopes,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")

@app.get("/drive/files")
def list_files(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    access_token: Optional[str] = Query(None)
):
    """
    List all files in Drive.
    Pass token via Authorization header or access_token query param.
    """
    token = extract_token(authorization, access_token)

    try:
        service = build_service_from_token(token)
        all_files = []
        page_token = None

        while True:
            results = service.files().list(
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, size, parents)",
                pageToken=page_token
            ).execute()

            files = results.get("files", [])
            for f in files:
                f["fullPath"] = build_file_path(service, f["id"])
                all_files.append(f)

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return {"files": all_files, "count": len(all_files)}

    except HttpError as e:
        status = e.resp.status if hasattr(e, "resp") else 500
        if status == 401:
            raise HTTPException(status_code=401, detail="Invalid or expired access token. Please provide a valid token.")
        elif status == 403:
            raise HTTPException(status_code=403, detail="Forbidden. Ensure your token has the correct Google Drive scopes.")
        else:
            raise HTTPException(status_code=status, detail=f"Google API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/drive/read_all")
def read_all_files(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    access_token: Optional[str] = Query(None)
):
    """
    Read all files in Drive and return Base64 encoded content with metadata.
    """
    token = extract_token(authorization, access_token)

    try:
        service = build_service_from_token(token)
        all_files = []
        page_token = None

        while True:
            results = service.files().list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, parents)",
                pageToken=page_token
            ).execute()

            files = results.get("files", [])
            for f in files:
                try:
                    f["fullPath"] = build_file_path(service, f["id"])
                    f["base64"] = get_file_as_base64(service, f["id"])
                    all_files.append(f)
                except Exception as inner_e:
                    f["error"] = str(inner_e)
                    all_files.append(f)

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return {"files": all_files, "count": len(all_files)}

    except HttpError as e:
        status = e.resp.status if hasattr(e, "resp") else 500
        if status == 401:
            raise HTTPException(status_code=401, detail="Invalid or expired access token. Please provide a valid token.")
        elif status == 403:
            raise HTTPException(status_code=403, detail="Forbidden. Ensure your token has the correct Google Drive scopes.")
        else:
            raise HTTPException(status_code=status, detail=f"Google API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


from googleapiclient.http import MediaIoBaseUpload

@app.post("/drive/upload")
async def upload_file(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    access_token: Optional[str] = Query(None),
    parent_id: Optional[str] = Query(None, description="Optional parent folder ID")
):
    """
    Upload a file to Google Drive.
    - Pass token via Authorization header or access_token query param.
    - Optionally specify a parent_id (folder ID).
    """
    token = extract_token(authorization, access_token)

    try:
        service = build_service_from_token(token)

        # Read file into memory
        file_content = await file.read()
        file_stream = io.BytesIO(file_content)

        # Metadata
        metadata = {"name": file.filename}
        if parent_id:
            metadata["parents"] = [parent_id]

        media = MediaIoBaseUpload(file_stream, mimetype=file.content_type, resumable=True)

        uploaded_file = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, name, mimeType, parents"
        ).execute()

        return {
            "message": "File uploaded successfully",
            "file": uploaded_file
        }

    except HttpError as e:
        status = e.resp.status if hasattr(e, "resp") else 500
        raise HTTPException(status_code=status, detail=f"Google API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")
