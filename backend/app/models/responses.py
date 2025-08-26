from pydantic import BaseModel

# Response model for file uploads
class UploadResponse(BaseModel):
    file_id: str          # Unique identifier for the uploaded file
    filename: str         # Original filename of the uploaded file
    status: str = "uploaded"  # Default status after upload

# Response model for text extraction from PDF
class ExtractResponse(BaseModel):
    file_id: str          # File identifier for the extracted document
    pages: int            # Total number of pages in the PDF
    is_encrypted: bool    # Flag indicating if the PDF is password protected/encrypted
    metadata: dict        # Metadata about the PDF (title, author, etc.)
    sample_text: str      # A sample snippet of extracted text (for preview/validation)

# Response model for processing jobs
class ProcessResponse(BaseModel):
    job_id: str           # Unique identifier for the processing job
    status: str           # Current status of the job (e.g., "pending", "processing", "done")

# Response model for job status checks
class StatusResponse(BaseModel):
    job_id: str           # Job identifier
    status: str           # Current job status
    result: dict | None = None  # Result of the job if completed, None otherwise
