import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import app.database.connection as db_conn
from app.models.scheduled_post import ScheduledPost
from app.scheduler.processor import process_scheduled_post
from app.services.analytics.service import AnalyticsService
from app.core.config import SCHEDULER_ENABLED, SCHEDULER_INTERVAL_SECONDS

logger = logging.getLogger(__name__)

# A flag to control the run loop gracefully
_scheduler_running = False
_scheduler_stop_event: asyncio.Event | None = None

async def run_scheduler():
    """
    Background worker that continually polls for due scheduled posts 
    and dispatches them for processing.
    """
    if not SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled in configuration. Worker will not start.")
        return

    global _scheduler_running, _scheduler_stop_event
    _scheduler_running = True
    _scheduler_stop_event = asyncio.Event()
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
        
        # Sleep for the configured interval before checking again, interruptible via stop_event
        if not _scheduler_running or (_scheduler_stop_event and _scheduler_stop_event.is_set()):
            break

        try:
            if _scheduler_stop_event:
                await asyncio.wait_for(_scheduler_stop_event.wait(), timeout=SCHEDULER_INTERVAL_SECONDS)
                # Event was set, exit cleanly
                break
            else:
                await asyncio.sleep(SCHEDULER_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            # Polling interval elapsed, continue loop
            pass
        except asyncio.CancelledError:
            logger.info("Scheduler sleep cancelled.")
            break

async def stop_scheduler():
    """Gracefully stop the scheduler run loop."""
    global _scheduler_running, _scheduler_stop_event
    _scheduler_running = False
    if _scheduler_stop_event:
        _scheduler_stop_event.set()
    logger.info("Scheduler shutdown requested.")

async def poll_and_process_jobs():
    """
    Polls the database for due jobs and claims them atomically.
    """
    now = datetime.now(timezone.utc)
    claimed_post_ids: list[int] = []
    
    async with db_conn.AsyncSessionLocal() as db:
        bind = db.get_bind()
        is_sqlite = bind.dialect.name == "sqlite"

        if not is_sqlite:
            # PostgreSQL row locking: SELECT ... FOR UPDATE SKIP LOCKED
            # Prevents multiple workers from acquiring the same post simultaneously
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
            
            if due_posts:
                logger.info(f"Scheduler found {len(due_posts)} due post(s). Claiming...")
                for post in due_posts:
                    post.status = "processing"
                    post.updated_at = datetime.now(timezone.utc)
                    claimed_post_ids.append(post.id)
                await db.commit()
        else:
            # SQLite does not support FOR UPDATE SKIP LOCKED.
            # Strategy: Query candidate due post IDs, then atomically update status
            # from 'scheduled' to 'processing'. Only the worker whose UPDATE affects > 0
            # rows successfully claims the post.
            stmt = (
                select(ScheduledPost.id)
                .where(
                    ScheduledPost.status == "scheduled",
                    ScheduledPost.scheduled_time <= now
                )
                .limit(10)
            )
            result = await db.execute(stmt)
            candidate_ids = result.scalars().all()

            for cid in candidate_ids:
                claim_stmt = (
                    update(ScheduledPost)
                    .where(
                        ScheduledPost.id == cid,
                        ScheduledPost.status == "scheduled"
                    )
                    .values(
                        status="processing",
                        updated_at=datetime.now(timezone.utc)
                    )
                )
                claim_res = await db.execute(claim_stmt)
                if claim_res.rowcount > 0:
                    claimed_post_ids.append(cid)

            if claimed_post_ids:
                await db.commit()
            else:
                await db.rollback()

    if not claimed_post_ids:
        return

    # Process each claimed job in its own independent session
    for post_id in claimed_post_ids:
        async with db_conn.AsyncSessionLocal() as job_db:
            result = await job_db.execute(select(ScheduledPost).where(ScheduledPost.id == post_id))
            refreshed_post = result.scalar_one_or_none()
            if not refreshed_post or refreshed_post.status != "processing":
                continue
            
            try:
                await process_scheduled_post(refreshed_post, job_db)
            except Exception as e:
                logger.error(f"Unhandled exception processing post {post_id}: {e}")
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
    
    post_ids_to_update: list[int] = []
    async with db_conn.AsyncSessionLocal() as db:
        # Find published posts
        stmt = (
            select(ScheduledPost.id)
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
        post_ids_to_update = list(result.scalars().all())
        
        if not post_ids_to_update:
            return
            
        logger.info(f"Scheduler found {len(post_ids_to_update)} post(s) for analytics collection.")
        
    for post_id in post_ids_to_update:
        async with db_conn.AsyncSessionLocal() as job_db:
            result = await job_db.execute(select(ScheduledPost).where(ScheduledPost.id == post_id))
            refreshed_post = result.scalar_one_or_none()
            if not refreshed_post:
                continue
            
            try:
                await AnalyticsService.collect_post_analytics(refreshed_post, job_db)
            except Exception as e:
                logger.error(f"Failed to collect analytics for post {post_id}: {e}")

