import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models.responses import UploadResponse

# Directory to store uploaded PDFs
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

# Create FastAPI router
router = APIRouter()

# -------------------------------
# Endpoint to upload PDF files
# -------------------------------
@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    """
    Upload a PDF file to the server and return a unique file ID.

    Args:
        file (UploadFile): PDF file uploaded by the client.

    Returns:
        UploadResponse: Contains file_id, original filename, and status.

    Raises:
        HTTPException: 400 if file is not a PDF.
    """
    # Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are accepted")

    # Generate a unique file ID
    file_id = str(uuid.uuid4())
    dest_path = UPLOAD_DIR / f"{file_id}.pdf"

    # Save uploaded file to disk
    try:
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()

    # Return structured response
    return UploadResponse(file_id=file_id, filename=file.filename)
