from pathlib import Path
from app.lib.socketio_server import sio
from app.core import llm_router
import asyncio

# Asynchronously processes a PDF document and updates job status in real-time
async def process_document(job_id, file_path: Path, jobs):
    """
    Process a PDF:
    1. Detect scanned vs text
    2. Route to LLM (LlamaParse / OpenAI / Gemini / Stub)
    3. Update job status in real-time via Socket.IO
    """
    try:
        # Step 0: Mark in-progress
        jobs[job_id]["status"] = "In-Progress"
        await sio.emit("job_update", {"job_id": job_id, "status": "In-Progress"})

        # Step 1: Detect if the PDF is scanned or text-based (offload to thread)
        is_scanned, pages = await asyncio.to_thread(
            llm_router.detect_if_scanned, file_path
        )

        # 🔹 Step 2: Move to validation phase (UI will show "Validating")
        jobs[job_id]["status"] = "Validating"
        await sio.emit("job_update", {"job_id": job_id, "status": "Validating"})

        # Optional small delay so the validating state is visible in the UI
        await asyncio.sleep(0.2)

        # Step 3: Route to the appropriate LLM provider
        llm_callable = llm_router.route_llm(
            pages=pages,
            sample_text="",  # empty because LlamaParse can read PDF directly
            is_scanned=is_scanned,
            file_path=file_path,
        )

        # Step 4: Call the LLM in a separate thread (non-blocking)
        llm_result = await asyncio.to_thread(llm_callable)

        # Step 5: Extract tables and provider info from the LLM result
        tables = llm_result.get("tables", [])
        provider = llm_result.get("provider", "unknown")
        is_stub = "(stub)" in provider

        # Step 6: Update job status and result as completed
        jobs[job_id]["status"] = "Completed"
        jobs[job_id]["result"] = {
            "pages": pages,
            "is_scanned": is_scanned,
            "llm_provider": provider,
            "llm_model": llm_result.get("model", "unknown"),
            "tables": tables,
            "table_count": len(tables),
            "table_titles": [t.get("title", f"Table {i+1}") for i, t in enumerate(tables)],
            "used_stub": is_stub,
        }

        # Emit real-time update to client
        await sio.emit(
            "job_update",
            {
                "job_id": job_id,
                "status": "Completed",
                "result": jobs[job_id]["result"],
            },
        )

    except Exception as e:
        # Handle errors: mark job as failed and notify clients
        jobs[job_id]["status"] = "Failed"
        jobs[job_id]["result"] = None
        await sio.emit("job_update", {"job_id": job_id, "status": "Failed"})
        print(f"[process_document] Job {job_id} failed: {e}")
