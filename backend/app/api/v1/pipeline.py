"""
OpenSpends NG — Pipeline Monitoring & Control API

GET  /v1/pipeline/health          — Overall pipeline health dashboard
GET  /v1/pipeline/runs            — Recent pipeline run history
GET  /v1/pipeline/runs/{run_id}   — Single run details
GET  /v1/pipeline/jobs            — Scheduled job info (APScheduler)
POST /v1/pipeline/trigger         — Manually trigger a pipeline run
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import PipelineRun, DataSourceRegistry
from app.services.dedup import get_pipeline_stats

router = APIRouter()


# ── Schemas (inline to avoid circular imports) ──

from pydantic import BaseModel


class PipelineHealthResponse(BaseModel):
    status: str
    total_runs: int
    success_count: int
    failed_count: int
    last_success_at: Optional[str] = None
    last_run_at: Optional[str] = None
    sources: list[dict]
    scheduled_jobs: list[dict]


class PipelineRunOut(BaseModel):
    id: int
    source: str
    status: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    records_found: int
    records_inserted: int
    records_updated: int
    records_skipped: int
    error_message: Optional[str] = None
    details: Optional[dict] = None

    class Config:
        from_attributes = True


class PipelineRunList(BaseModel):
    data: list[PipelineRunOut]
    total: int
    page: int
    page_size: int


class PipelineTriggerRequest(BaseModel):
    source: str = Query(..., description="Data source to trigger: 'govspend', 'pdf_parser', 'full'")


class PipelineTriggerResponse(BaseModel):
    message: str
    source: str
    note: str = "Pipeline run initiated in background"


# ── Endpoints ──

@router.get("/health", response_model=PipelineHealthResponse)
async def pipeline_health(db: Session = Depends(get_db)):
    """
    Pipeline health dashboard.

    Shows recent success/failure rates, last sync times per source,
    and scheduled job status.
    """
    # Aggregate stats from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_runs = db.query(PipelineRun).filter(PipelineRun.started_at >= thirty_days_ago).all()

    total = len(recent_runs)
    successes = sum(1 for r in recent_runs if r.status == "success")
    failures = sum(1 for r in recent_runs if r.status == "failed")

    # Last success and run times
    all_runs_ordered = (
        db.query(PipelineRun)
        .order_by(PipelineRun.started_at.desc())
        .all()
    )

    last_run_at = all_runs_ordered[0].started_at.isoformat() if all_runs_ordered else None
    last_success = next((r for r in all_runs_ordered if r.status == "success"), None)
    last_success_at = last_success.started_at.isoformat() if last_success else None

    # Per-source stats
    sources = []
    for source_name in ["govspend", "pdf_parser", "bpp", "icpc"]:
        source_runs = [r for r in recent_runs if r.source == source_name]
        if source_runs:
            latest = max(source_runs, key=lambda r: r.started_at)
            sources.append({
                "name": source_name,
                "last_run": latest.started_at.isoformat() if latest.started_at else None,
                "last_status": latest.status,
                "run_count_30d": len(source_runs),
                "fail_count_30d": sum(1 for r in source_runs if r.status == "failed"),
            })

    # Overall status determination
    overall_status = "healthy"
    if total == 0:
        overall_status = "no_runs"
    elif failures > successes:
        overall_status = "degraded"
    elif last_success_at:
        last_success_dt = datetime.fromisoformat(last_success_at)
        if datetime.utcnow() - last_success_dt > timedelta(days=7):
            overall_status = "stale"

    # Scheduled jobs
    try:
        from app.services.scheduler import get_job_info
        jobs = get_job_info()
    except Exception:
        jobs = []

    return PipelineHealthResponse(
        status=overall_status,
        total_runs=total,
        success_count=successes,
        failed_count=failures,
        last_success_at=last_success_at,
        last_run_at=last_run_at,
        sources=sources,
        scheduled_jobs=jobs,
    )


@router.get("/runs", response_model=PipelineRunList)
async def list_pipeline_runs(
    source: Optional[str] = Query(None, description="Filter by source"),
    status: Optional[str] = Query(None, description="Filter by status: success, failed, running"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List recent pipeline runs with optional filters."""
    query = db.query(PipelineRun)

    if source:
        query = query.filter_by(source=source)
    if status:
        query = query.filter_by(status=status)

    total = query.count()
    runs = (
        query.order_by(PipelineRun.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PipelineRunList(
        data=[PipelineRunOut.model_validate(r) for r in runs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/runs/{run_id}", response_model=PipelineRunOut)
async def get_pipeline_run(run_id: int, db: Session = Depends(get_db)):
    """Get details of a specific pipeline run."""
    run = db.query(PipelineRun).filter_by(id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Pipeline run {run_id} not found")
    return PipelineRunOut.model_validate(run)


@router.get("/jobs")
async def list_scheduled_jobs():
    """List APScheduler jobs and their next run times."""
    try:
        from app.services.scheduler import get_job_info
        return {"jobs": get_job_info()}
    except Exception as e:
        return {"jobs": [], "error": str(e)}


@router.post("/trigger", response_model=PipelineTriggerResponse)
async def trigger_pipeline(
    request: PipelineTriggerRequest,
    background_tasks: BackgroundTasks,
):
    """
    Manually trigger a pipeline run in the background.

    Supported sources:
    - `govspend` — Scrape GovSpend and ingest payments
    - `full`     — Run all configured pipelines
    """
    source = request.source.lower().strip()

    if source == "govspend":
        from app.services.pipeline import run_govspend_pipeline
        background_tasks.add_task(run_govspend_pipeline)
    elif source == "full":
        from app.services.pipeline import run_full_pipeline
        background_tasks.add_task(run_full_pipeline)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown source '{source}'. Use 'govspend' or 'full'.",
        )

    return PipelineTriggerResponse(
        message=f"Pipeline '{source}' triggered",
        source=source,
    )
