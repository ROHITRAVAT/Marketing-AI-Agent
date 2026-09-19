import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.connection as db_conn
from app.models.scheduled_post import ScheduledPost
from app.scheduler.processor import process_scheduled_post
from app.services.analytics.service import AnalyticsService
from app.core.config import SCHEDULER_ENABLED, SCHEDULER_INTERVAL_SECONDS

logger = logging.getLogger(__name__)

# A flag to control the run loop gracefully
_scheduler_running = False

async def run_scheduler():
    """
    Background worker that continually polls for due scheduled posts 
    and dispatches them for processing.
    """
    if not SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled in configuration. Worker will not start.")
        return

    global _scheduler_running
    _scheduler_running = True
    logger.info(f"Scheduler started. Polling every {SCHEDULER_INTERVAL_SECONDS} seconds.")

    while _scheduler_running:
        try:
            await asyncio.gather(
                poll_and_process_jobs(),
                poll_and_collect_analytics()
            )
        except asyncio.CancelledError:
            logger.info("Scheduler cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}", exc_info=True)
        
        # Sleep for the configured interval before checking again
        # We use asyncio.sleep which can be interrupted gracefully
        try:
            await asyncio.sleep(SCHEDULER_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            logger.info("Scheduler sleep cancelled.")
            break

async def stop_scheduler():
    """Gracefully stop the scheduler run loop."""
    global _scheduler_running
    _scheduler_running = False
    logger.info("Scheduler shutdown requested.")

async def poll_and_process_jobs():
    """
    Polls the database for due jobs and claims them atomically.
    """
    # 1. Find jobs that are due
    now = datetime.now(timezone.utc)
    
    async with db_conn.AsyncSessionLocal() as db:
        # Atomic lock: SELECT ... FOR UPDATE SKIP LOCKED
        # This prevents multiple workers from processing the same post simultaneously.
        stmt = (
            select(ScheduledPost)
            .where(
                ScheduledPost.status == "scheduled",
                ScheduledPost.scheduled_time <= now
            )
            .with_for_update(skip_locked=True)
            .limit(10)  # Batch size
        )
        
        result = await db.execute(stmt)
        due_posts = result.scalars().all()
        
        if not due_posts:
            return
            
        logger.info(f"Scheduler found {len(due_posts)} due post(s). Claiming...")
        
        # 2. Claim the jobs by updating their status to 'processing'
        # We must commit the transaction to release the lock but hold the new status
        for post in due_posts:
            post.status = "processing"
            post.updated_at = datetime.now(timezone.utc)
            
        await db.commit()

    # 3. Process the claimed jobs outside the main lock transaction
    for post in due_posts:
        # We start a new session for each job to ensure independence
        async with db_conn.AsyncSessionLocal() as job_db:
            # Re-fetch the post in this new session context
            result = await job_db.execute(select(ScheduledPost).where(ScheduledPost.id == post.id))
            refreshed_post = result.scalar_one()
            
            try:
                await process_scheduled_post(refreshed_post, job_db)
            except Exception as e:
                logger.error(f"Unhandled exception processing post {post.id}: {e}")
                refreshed_post.status = "failed"
                refreshed_post.error_message = str(e)
                refreshed_post.updated_at = datetime.now(timezone.utc)
                await job_db.commit()

async def poll_and_collect_analytics():
    """
    Polls for published posts that need analytics updates and collects them.
    We target posts published in the last 30 days that haven't been updated in the last 6 hours.
    """
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    
    async with db_conn.AsyncSessionLocal() as db:
        # Find published posts
        stmt = (
            select(ScheduledPost)
            .where(
                ScheduledPost.status == "published",
                ScheduledPost.published_at >= now - timedelta(days=30)
            )
            .where(
                (ScheduledPost.last_analytics_collected_at == None) | 
                (ScheduledPost.last_analytics_collected_at < now - timedelta(hours=6))
            )
            .limit(20)  # Batch size
        )
        
        result = await db.execute(stmt)
        posts_to_update = result.scalars().all()
        
        if not posts_to_update:
            return
            
        logger.info(f"Scheduler found {len(posts_to_update)} post(s) for analytics collection.")
        
    for post in posts_to_update:
        async with db_conn.AsyncSessionLocal() as job_db:
            result = await job_db.execute(select(ScheduledPost).where(ScheduledPost.id == post.id))
            refreshed_post = result.scalar_one()
            
            try:
                await AnalyticsService.collect_post_analytics(refreshed_post, job_db)
            except Exception as e:
                logger.error(f"Failed to collect analytics for post {post.id}: {e}")

