# Phase 1 – Backend Foundations (FastAPI basics)

This folder is a minimal FastAPI backend that lets you **upload a PDF** and **extract basic metadata**.

## 1) Create & activate a virtualenv (Windows PowerShell)

```powershell
cd backend
py -3.13 -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> If `py` isn't available, try: `python -m venv venv` then `venv\Scripts\activate`.

## 2) Run the API (dev mode with auto-reload)
```powershell
uvicorn main:app --reload
```
- Server: http://127.0.0.1:8000
- Docs (Swagger UI): http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 3) Test endpoints

### Upload a PDF
**Swagger UI** → `POST /upload` (select a file).  
Or with curl (PowerShell has both `curl` and `curl.exe`; use `curl.exe` to avoid alias issues):

```powershell
curl.exe -F "file=@C:\\Path\\To\\Your\\Document3.pdf" http://127.0.0.1:8000/upload
```
**Response example:**
```json
{
  "file_id": "60b1d2e1-8a9b-4c3e-9b61-78b20f4d9d2a",
  "filename": "Document3.pdf",
  "status": "uploaded"
}
```

### Extract metadata
Copy the `file_id` from upload and call:
```powershell
curl.exe "http://127.0.0.1:8000/extract?file_id=60b1d2e1-8a9b-4c3e-9b61-78b20f4d9d2a"
```
**Response example:**
```json
{
  "file_id": "60b1d2e1-8a9b-4c3e-9b61-78b20f4d9d2a",
  "pages": 12,
  "is_encrypted": false,
  "metadata": {
    "title": "Sample Report",
    "author": "Jane Doe",
    "creator": null,
    "producer": "PDF Producer 1.7",
    "subject": null
  },
  "sample_text": "This report provides..."
}
```

## Notes
- Files are stored under `backend/uploads/` using a generated `file_id`.
- For simple/clean CORS during development, all origins are allowed. Tighten this later.
- We use **pypdf** (maintained successor to PyPDF2) for text & metadata.
- If a PDF is scanned or encrypted, `sample_text` can be empty and `is_encrypted` may be `true`.

Doc LLM Pipeline – Phase 2
--------------------------------
FastAPI backend for document upload, metadata extraction,
and asynchronous processing with job status tracking.

Features:
    - Upload PDFs
    - Extract metadata & sample text
    - Background job handling (simulated LLM/processing step)
    - Job status tracking
    - Health check endpoint
