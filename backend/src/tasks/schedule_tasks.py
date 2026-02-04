"""Celery tasks for schedule synchronization.

Note:
    These tasks are prepared but not activated until Celery is fully configured.
    To use, uncomment the Celery app initialization and beat schedule.

Usage (when Celery is configured):
    # Start Celery worker
    celery -A src.tasks.schedule_tasks worker --loglevel=info

    # Start Celery beat (for periodic tasks)
    celery -A src.tasks.schedule_tasks beat --loglevel=info

    # Or start both together
    celery -A src.tasks.schedule_tasks worker --beat --loglevel=info
"""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any

# Celery is optional - only import if available
try:
    from celery import Celery

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    Celery = None  # type: ignore[misc, assignment]

from src.config import settings

logger = logging.getLogger(__name__)

# Windows event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def get_celery_app() -> Any:
    """Get or create Celery application.

    Returns:
        Celery app instance or None if Celery is not available.
    """
    if not CELERY_AVAILABLE:
        logger.warning("Celery is not installed. Background tasks are disabled.")
        return None

    app = Celery(
        "studyhelper",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )

    # Celery configuration
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Europe/Moscow",
        enable_utc=True,
        # Task execution settings
        task_soft_time_limit=300,  # 5 minutes
        task_time_limit=360,  # 6 minutes hard limit
        # Retry settings
        task_acks_late=True,
        task_reject_on_worker_lost=True,
    )

    # Beat schedule (periodic tasks) - commented until Celery is fully configured
    # app.conf.beat_schedule = {
    #     "sync-schedule-every-6-hours": {
    #         "task": "src.tasks.schedule_tasks.sync_schedule_task",
    #         "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    #         "args": (False,),  # force=False
    #     },
    # }

    return app


# Create app instance (will be None if Celery not available)
celery_app = get_celery_app()


async def _async_sync_schedule(force: bool = False) -> dict[str, Any]:
    """Async helper for sync_schedule_task.

    Args:
        force: Force sync even if hash unchanged.

    Returns:
        Sync result dictionary.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    from src.services import schedule as schedule_service

    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as db:
            result = await schedule_service.sync_schedule(db, force=force)
            return result
    finally:
        await engine.dispose()


def sync_schedule_task(force: bool = False) -> dict[str, Any]:
    """Synchronize schedule from OmGU website.

    This is the main Celery task for schedule synchronization.
    Can be called manually or via periodic beat schedule.

    Args:
        force: Force sync even if content hash unchanged.

    Returns:
        Dictionary with sync result:
            - success: bool
            - changed: bool
            - entries_count: int
            - content_hash: str (if success)
            - message: str (error message if not success)
    """
    logger.info("Starting schedule sync task (force=%s)", force)

    try:
        result = asyncio.run(_async_sync_schedule(force))
        logger.info(
            "Schedule sync completed: changed=%s, entries=%d",
            result.get("changed"),
            result.get("entries_count", 0),
        )
        return result
    except Exception as e:
        logger.error("Schedule sync failed: %s", e, exc_info=True)
        return {
            "success": False,
            "changed": False,
            "entries_count": 0,
            "message": str(e),
        }


# Register task with Celery if available
if celery_app is not None:
    sync_schedule_task = celery_app.task(
        name="src.tasks.schedule_tasks.sync_schedule_task",
        bind=False,
        max_retries=3,
        default_retry_delay=60,
    )(sync_schedule_task)
