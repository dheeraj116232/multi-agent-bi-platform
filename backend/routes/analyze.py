"""
routes/analyze.py — Production FastAPI route with Neon PostgreSQL
"""

import os, uuid, shutil, time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.graph import pipeline
from database import get_db, JobRecord, SessionLocal

router = APIRouter(prefix="/api", tags=["analyze"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".csv", ".tsv", ".txt",
    ".xlsx", ".xls", ".xlsm", ".xlsb", ".ods",
    ".json", ".jsonl",
    ".parquet",
    ".xml",
    ".zip",
}

AGENT_PROGRESS = {
    "cleaner":    20,
    "analytics":  40,
    "visualizer": 60,
    "forecaster": 80,
    "reporter":   95,
}


# ── Upload + run pipeline ─────────────────────────────────────────────────────

@router.post("/analyze")
async def analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )

    # Save uploaded file
    job_id    = str(uuid.uuid4())
    filename  = f"{job_id}{ext}"
    file_path = f"{UPLOAD_DIR}/{filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Save job to database
    job = JobRecord(
        id=job_id,
        filename=file.filename,
        status="pending",
        progress_pct=0,
    )
    db.add(job)
    db.commit()

    background_tasks.add_task(_run_pipeline, job_id, file_path, file.filename)
    return {"job_id": job_id, "status": "pending", "message": "Analysis started"}


# ── Poll job status ───────────────────────────────────────────────────────────

@router.get("/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id":        job_id,
        "status":        job.status,
        "current_agent": job.current_agent,
        "progress_pct":  job.progress_pct,
        "filename":      job.filename,
    }

    if job.status == "done":
        response["result"] = {
            "cleaning_report": job.cleaning_report,
            "file_meta":       job.file_meta,
            "analytics":       job.analytics,
            "forecast":        job.forecast,
            "chart_count":     len(job.chart_paths or []),
            "chart_paths":     job.chart_paths,
            "chart_metadata":  job.chart_metadata,
            "report_text":     job.report_text,
            "pdf_path":        job.pdf_path,
            "errors":          job.errors_list or [],
            "warnings":        job.warnings or [],
            "processing_time": job.processing_time or {},
        }

    if job.status == "failed":
        response["error"] = job.error

    return response


# ── Download PDF ──────────────────────────────────────────────────────────────

@router.get("/download/pdf/{job_id}")
async def download_pdf(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job or job.status != "done":
        raise HTTPException(status_code=404, detail="Report not ready")

    pdf_path = job.pdf_path
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"executive_report_{job_id[:8]}.pdf",
    )


# ── Get chart image ───────────────────────────────────────────────────────────

@router.get("/chart/{job_id}/{chart_index}")
async def get_chart(job_id: str, chart_index: int, db: Session = Depends(get_db)):
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job or job.status != "done":
        raise HTTPException(status_code=404, detail="Charts not ready")

    charts = job.chart_paths or []
    if chart_index >= len(charts):
        raise HTTPException(status_code=404, detail="Chart index out of range")

    chart_path = charts[chart_index]
    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="Chart file not found")

    return FileResponse(chart_path, media_type="image/png")


# ── List all jobs ─────────────────────────────────────────────────────────────

@router.get("/jobs")
async def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobRecord).order_by(JobRecord.created_at.desc()).limit(50).all()
    return [
        {
            "job_id":     j.id,
            "filename":   j.filename,
            "status":     j.status,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]


# ── Background pipeline runner ────────────────────────────────────────────────

def _run_pipeline(job_id: str, file_path: str, original_filename: str):
    db = SessionLocal()
    try:
        # Mark as running
        job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
        job.status = "running"
        db.commit()

        initial_state = {
            "raw_file_path":    file_path,
            "filename":         original_filename,
            "file_meta":        None,
            "clean_df":         None,
            "cleaning_report":  None,
            "analytics_result": None,
            "column_map":       None,
            "chart_paths":      None,
            "chart_metadata":   None,
            "forecast_result":  None,
            "report_text":      None,
            "pdf_path":         None,
            "errors":           [],
            "warnings":         [],
            "current_agent":    None,
            "processing_time":  {},
        }

        # Stream steps — update DB progress live
        result = None
        for step in pipeline.stream(initial_state):
            agent_name = list(step.keys())[0]
            job.current_agent = agent_name
            job.progress_pct  = AGENT_PROGRESS.get(agent_name, 50)
            db.commit()
            result = step[agent_name]

        # If stream gave us last state use it, otherwise invoke fresh
        if result is None:
            result = pipeline.invoke(initial_state)

        # Save full result to database
        job.status          = "done"
        job.progress_pct    = 100
        job.current_agent   = "reporter"
        job.cleaning_report = result.get("cleaning_report")
        job.file_meta       = result.get("file_meta")
        job.analytics       = {
            "summary":     result.get("analytics_result", {}).get("summary"),
            "revenue":     result.get("analytics_result", {}).get("revenue"),
            "product":     result.get("analytics_result", {}).get("product"),
            "region":      result.get("analytics_result", {}).get("region"),
            "time_series": result.get("analytics_result", {}).get("time_series"),
            "customer":    result.get("analytics_result", {}).get("customer"),
        }
        job.forecast        = result.get("forecast_result")
        job.chart_paths     = result.get("chart_paths")
        job.chart_metadata  = result.get("chart_metadata")
        job.report_text     = result.get("report_text")
        job.pdf_path        = result.get("pdf_path")
        job.processing_time = result.get("processing_time")
        job.warnings        = result.get("warnings", [])
        job.errors_list     = result.get("errors", [])
        db.commit()

    except Exception as e:
        import traceback
        print(f"Pipeline failed for job {job_id}: {e}\n{traceback.format_exc()}")
        try:
            job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
            if job:
                job.status = "failed"
                job.error  = str(e)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()