from fastapi import APIRouter, HTTPException, Query
from app.models.responses import ExtractResponse
from app.core.jobs_store import jobs  # import shared jobs dict

router = APIRouter()

@router.get("/extract", response_model=ExtractResponse)
def extract(file_id: str = Query(...)):
    # Find the job with this file_id
    job_entry = None
    for job in jobs.values():
        if job.get("file_id") == file_id:
            job_entry = job
            break

    if not job_entry or not job_entry.get("result"):
        raise HTTPException(status_code=404, detail="Result not found. Processing may still be in progress.")

    result = job_entry["result"]

    return ExtractResponse(
        file_id=file_id,
        pages=result.get("pages"),
        is_encrypted=result.get("is_scanned"),
        metadata=result.get("metadata", {}),
        sample_text=result.get("sample_text", ""),
        tables=result.get("tables", []),
        llm_provider=result.get("llm_provider"),
        llm_model=result.get("llm_model"),
    )
