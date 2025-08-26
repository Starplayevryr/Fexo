# app/api/routes_status.py
from fastapi import APIRouter, HTTPException
from app.models.responses import StatusResponse
from app.core.jobs_store import jobs  # import shared jobs dict

# Create FastAPI router
router = APIRouter()

# -------------------------------
# Endpoint to get the status of a processing job
# -------------------------------

@router.get("/status/{job_id}", response_model=StatusResponse)
def get_status(job_id: str):
    """
    Retrieve the status and result of a processing job by job ID.

    Args:
        job_id (str): Unique identifier of the job.

    Returns:
        StatusResponse: Contains job_id, current status, and result (if completed).

    Raises:
        HTTPException: 404 if the job ID does not exist.
    """
    job_entry = jobs.get(job_id)
    if not job_entry:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Return structured response using Pydantic model
    return StatusResponse(
        job_id=job_id,
        status=job_entry.get("status"),
        result=job_entry.get("result")
    )
