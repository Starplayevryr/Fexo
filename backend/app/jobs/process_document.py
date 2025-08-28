from pathlib import Path
from app.lib.socketio_server import sio
from app.core import llm_router, pdf_utils
from app.core.keywords import contains_financial_keywords
from app.core.jobs_store import jobs
import asyncio

async def process_document(job_id, file_path: Path, jobs):
    try:
        # Step 0: In-Progress
        jobs[job_id]["status"] = "In-Progress"
        await sio.emit("job_update", {"job_id": job_id, "status": "In-Progress"})
        print(f"[{job_id}] Step 0: In-Progress")

        # Step 1: Detect scanned PDF
        is_scanned, page_count, pages = await asyncio.to_thread(pdf_utils.detect_if_scanned, file_path)
        print(f"[{job_id}] Step 1: scanned detection done")

        # Step 2: Sample text for LLM
        sample_text = "\n".join(pages[:3])[:5000] #just to check for inital analysis
        has_financial_terms = contains_financial_keywords(sample_text)
        print(f"[{job_id}] Step 2: sample text extracted")

        # Step 3: Route to LLM
        llm_info = llm_router.route_llm(
            pages=pages, #entire pages in pdf
            sample_text=sample_text,
            is_scanned=is_scanned,
            file_path=file_path
        )
        llm_callable = llm_info["func"]
        llm_result = await asyncio.to_thread(llm_callable)
        print(f"[{job_id}] Step 3: LLM routing done")

        # Step 4: Filter tables
        tables = llm_result.get("tables", [])
        clean_tables = []
        for i, t in enumerate(tables):
            rows = [row for row in t.get("rows", []) if row.strip()]
            clean_tables.append({
                "title": t.get("title") or f"Table (Page {i+1})",
                "page": t.get("page") or (i+1 if i < len(pages) else None),
                "rows": rows
            })
        print(f"[{job_id}] Step 4: table filtering done")

        # Step 5: Validation
        jobs[job_id]["status"] = "Validating"
        await sio.emit("job_update", {"job_id": job_id, "status": "Validating"})
        validation_passed = all(len(t["rows"]) > 0 for t in clean_tables)
        if not validation_passed:
            raise ValueError("Validation failed: one or more tables are empty")
        print(f"[{job_id}] Step 5: validation done")

        # Step 6: Save results in JSON-friendly format
        jobs[job_id]["status"] = "Completed"
        jobs[job_id]["result"] = {
            "pages": pages,  # list of page text
            "is_scanned": is_scanned,
            "llm_provider": llm_result.get("provider", "unknown"),
            "llm_model": llm_result.get("model", "unknown"),
            "tables": clean_tables,  # list of dicts: {title, page, rows}
            "table_count": len(clean_tables),
            "table_titles": [t["title"] for t in clean_tables],
            "used_stub": "(stub)" in llm_result.get("provider", ""),
            "has_financial_terms": has_financial_terms,
            "validation_passed": validation_passed
        }

        # Emit final result
        await sio.emit(
            "job_update",
            {"job_id": job_id, "status": "Completed", "result": jobs[job_id]["result"]}
        )
        print(f"[{job_id}] Step 6: result assigned & emitted")

    except Exception as e:
        jobs[job_id]["status"] = "Failed"
        jobs[job_id]["result"] = {
            "error": str(e)
        }
        await sio.emit("job_update", {"job_id": job_id, "status": "Failed", "result": jobs[job_id]["result"]})
        print(f"[process_document] Job {job_id} failed: {e}")
