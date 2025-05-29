import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

from ...services.summarizer import generate_daily_summary
from ...config import settings

logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = None

def init_scheduler() -> AsyncIOScheduler:
    """Initialize and start the scheduler."""
    global scheduler
    
    if scheduler and scheduler.running:
        return scheduler
    
    logger.info("Initializing scheduler...")
    
    scheduler = AsyncIOScheduler(timezone=pytz.UTC)
    
    # Add the daily summary job
    scheduler.add_job(
        generate_daily_summary,
        CronTrigger.from_crontab(settings.SUMMARY_SCHEDULE, timezone=pytz.UTC),
        id="daily_summary",
        name="Generate daily summary of notes",
        replace_existing=True,
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info(f"Scheduler started with job: {scheduler.get_job('daily_summary')}")
    
    return scheduler

async def shutdown_scheduler(scheduler: AsyncIOScheduler):
    """Shutdown the scheduler gracefully."""
    if scheduler and scheduler.running:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)

async def trigger_summary_manually():
    """Manually trigger the summary generation."""
    if not scheduler or not scheduler.running:
        raise RuntimeError("Scheduler is not running")
    
    job = scheduler.get_job("daily_summary")
    if not job:
        raise ValueError("Daily summary job not found")
    
    # Trigger the job now
    job.modify(next_run_time=datetime.now(pytz.UTC))
    return {"status": "success", "message": "Summary generation triggered manually"}

def get_scheduled_jobs():
    """Get all scheduled jobs."""
    if not scheduler:
        return []
    return [{
        "id": job.id,
        "name": job.name,
        "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
        "trigger": str(job.trigger) if job.trigger else None,
    } for job in scheduler.get_jobs()]
