from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from app.db.database import SessionLocal
from app.services.ai_agent import refresh_all_courses

logger = logging.getLogger(__name__)

# Create the scheduler instance
scheduler = AsyncIOScheduler()

def run_refresh_job():
    """Wrapper function to create a DB session and run the refresh."""
    logger.info("Triggering scheduled refresh job...")
    db = SessionLocal()
    try:
        refresh_all_courses(db)
    finally:
        db.close()

def start_scheduler():
    """Starts the APScheduler and adds the 15-day job."""
    if not scheduler.running:
        # Run every 15 days
        scheduler.add_job(
            run_refresh_job,
            trigger=IntervalTrigger(days=15),
            id="refresh_course_questions_job",
            name="Refresh questions for all courses every 15 days",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("APScheduler started. Question refresh job scheduled every 15 days.")

def stop_scheduler():
    """Stops the APScheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
