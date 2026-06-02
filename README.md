# google-drive-automation-api
Google Drive Management API built with FastAPI, OAuth2, and Google Drive API for authentication, file listing, reading, and uploading.

# Google Drive Management API with FastAPI

## Overview

Google Drive Management API is a FastAPI-based backend application that integrates with Google Drive using OAuth 2.0 authentication. The project allows users to authenticate with their Google account, access Drive files, upload files, retrieve file metadata, and read file contents through RESTful APIs.

This project demonstrates cloud integration, secure authentication, API development, and file management using modern Python frameworks and Google Cloud services.

---

## Features

### Authentication

* Google OAuth 2.0 Authentication
* Secure Access Token Generation
* Refresh Token Support
* User Authorization Flow

### File Management

* List all Google Drive files
* Retrieve file metadata
* Generate complete file paths
* Read file contents
* Upload files to Google Drive
* Access files using REST APIs

### API Features

* FastAPI-based RESTful architecture
* JSON responses
* Error handling and validation
* Token-based authorization
* Scalable and modular design

---

## Technologies Used

* Python
* FastAPI
* Google Drive API
* Google OAuth 2.0
* Google API Python Client
* Pydantic
* Uvicorn
* REST APIs

---

## Project Structure

```text
google-drive-api-fastapi/
│
├── app.py
├── requirements.txt
├── credentials.example.json
├── .gitignore
├── README.md
└── screenshots/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/google-drive-api-fastapi.git

cd google-drive-api-fastapi
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Google Credentials

1. Create a project in Google Cloud Console.
2. Enable Google Drive API.
3. Create OAuth Client Credentials.
4. Download credentials JSON.
5. Save the file as:

```text
credentials.json
```

---

## Run Application

```bash
uvicorn app:app --reload
```

Application will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically generates API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Available Endpoints

### Google Authentication

```http
POST /google/auth
```

Authenticate with Google and generate access tokens.

### List Drive Files

```http
GET /drive/files
```

Returns all files available in Google Drive.

### Read All Files

```http
GET /drive/read_all
```

Reads files and returns metadata with Base64 encoded content.

### Upload File

```http
POST /drive/upload
```

Uploads files directly to Google Drive.

---

## Skills Demonstrated

* FastAPI Development
* REST API Design
* Google Drive API Integration
* OAuth 2.0 Authentication
* Cloud Application Development
* Backend Development
* Secure File Handling
* API Security
* Python Programming

---

## Future Enhancements

* Folder Creation APIs
* File Deletion APIs
* File Sharing Functionality
* User Management
* Database Integration
* JWT Authentication
* Docker Deployment

---

## Disclaimer

This project is developed for educational, learning, and portfolio purposes. Users should follow Google's API usage policies and security best practices when deploying the application.
