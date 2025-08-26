import uuid
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.jobs.process_document import process_document
from app.core.jobs_store import jobs  # shared jobs dict

# Directory to store uploaded PDFs
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter()

class ProcessRequest(BaseModel):
    file_id: str  # Unique identifier of the file to process


async def _run_process(job_id: str, file_path: Path, jobs: dict):
    """
    Wrapper around process_document to catch and log errors
    so they don't crash silently.
    """
    try:
        await process_document(job_id, file_path, jobs)
    except Exception as e:
        jobs[job_id]["status"] = "Failed"
        jobs[job_id]["result"] = None
        print(f"[routes_process] Job {job_id} crashed: {e}")


@router.post("/process")
async def process_file(request: ProcessRequest):
    """
    Start processing a PDF file asynchronously and return a job ID.
    """
    file_id = request.file_id
    file_path = UPLOAD_DIR / f"{file_id}.pdf"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Generate unique job ID
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "In-Progress", "file_id": file_id, "result": None}

    # ✅ Schedule async processing safely with error handling
    asyncio.create_task(_run_process(job_id, file_path, jobs))

    return {"job_id": job_id, "status": "In-Progress"}
