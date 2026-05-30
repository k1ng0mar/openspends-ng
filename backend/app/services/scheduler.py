"""
OpenSpends NG — APScheduler Background Task Runner

Schedules periodic execution of data ingestion pipelines.
Started as a FastAPI lifespan background task.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def _run_govspend_sync():
    """Wrapper to run GovSpend pipeline from scheduler."""
    from app.services.pipeline import run_govspend_pipeline
    try:
        result = run_govspend_pipeline()
        logger.info(f"Scheduled GovSpend sync result: {result.get('status')}")
    except Exception as e:
        logger.error(f"Scheduled GovSpend sync failed: {e}")


def _run_full_sync():
    """Wrapper to run all pipelines from scheduler."""
    from app.services.pipeline import run_full_pipeline
    try:
        results = run_full_pipeline()
        logger.info(f"Scheduled full sync results: {results}")
    except Exception as e:
        logger.error(f"Scheduled full sync failed: {e}")


def start_scheduler():
    """Register all scheduled jobs and start the scheduler."""
    if scheduler.running:
        logger.warning("Scheduler already running")
        return

    # GovSpend: run daily at 2 AM UTC
    scheduler.add_job(
        _run_govspend_sync,
        trigger=CronTrigger(hour=2, minute=0),
        id="govspend_daily",
        name="GovSpend Daily Sync",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )

    # Full pipeline (all sources): run weekly on Monday at 3 AM UTC
    scheduler.add_job(
        _run_full_sync,
        trigger=CronTrigger(day_of_week="mon", hour=3, minute=0),
        id="full_pipeline_weekly",
        name="Full Pipeline Weekly Sync",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started with {len(scheduler.get_jobs())} jobs: "
        f"{[j.name for j in scheduler.get_jobs()]}"
    )


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def get_job_info() -> list[dict]:
    """Return information about scheduled jobs."""
    return [
        {
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        }
        for job in scheduler.get_jobs()
    ]
