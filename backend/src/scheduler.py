"""Schedule auto-sync via APScheduler with Redis distributed lock."""

from __future__ import annotations

import contextlib
import logging
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from redis.asyncio import Redis
from redis.exceptions import LockNotOwnedError

from src.config import settings
from src.database import get_session_maker
from src.metrics import SCHEDULE_SYNC_DURATION_SECONDS, SCHEDULE_SYNC_TOTAL

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None
_redis: Redis | None = None

LOCK_KEY = "studyhelper:schedule_sync_lock"


async def _get_redis() -> Redis:
    """Get or create async Redis client.

    Resets the cached client if the connection is broken,
    so the next call will create a fresh one.
    """
    global _redis
    if _redis is not None:
        try:
            await _redis.ping()
        except Exception:
            logger.warning("Redis connection lost, reconnecting...")
            with contextlib.suppress(Exception):
                await _redis.aclose()
            _redis = None

    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def _sync_schedule_with_lock() -> None:
    """Run schedule sync with Redis distributed lock.

    Acquires a non-blocking Redis lock so that only one worker
    runs sync at a time. If the lock is already held, this
    invocation is skipped silently.
    """
    redis = await _get_redis()
    lock = redis.lock(
        LOCK_KEY,
        timeout=settings.schedule_sync_lock_ttl_seconds,
        blocking=False,
    )

    acquired = await lock.acquire()
    if not acquired:
        logger.info("Schedule auto-sync skipped: another worker holds the lock")
        SCHEDULE_SYNC_TOTAL.labels(status="skipped").inc()
        return

    start = time.perf_counter()
    try:
        logger.info("Schedule auto-sync started")

        from src.services.schedule import sync_schedule

        session_maker = get_session_maker()
        async with session_maker() as db:
            result = await sync_schedule(db)

        duration = time.perf_counter() - start
        SCHEDULE_SYNC_DURATION_SECONDS.observe(duration)

        if result.get("success"):
            SCHEDULE_SYNC_TOTAL.labels(status="success").inc()
            logger.info(
                "Schedule auto-sync completed: changed=%s, entries=%s",
                result.get("changed"),
                result.get("entries_count"),
            )
        else:
            SCHEDULE_SYNC_TOTAL.labels(status="success").inc()
            logger.warning(
                "Schedule auto-sync finished with issues: %s",
                result.get("message"),
            )
    except Exception:
        SCHEDULE_SYNC_TOTAL.labels(status="error").inc()
        logger.exception("Schedule auto-sync failed")
    finally:
        try:
            await lock.release()
        except LockNotOwnedError:
            logger.warning(
                "Schedule sync lock expired before release (TTL=%ds)",
                settings.schedule_sync_lock_ttl_seconds,
            )


async def start_scheduler() -> None:
    """Create and start the APScheduler instance.

    Does nothing if schedule_sync_enabled is False.
    """
    global _scheduler

    if not settings.schedule_sync_enabled:
        logger.info("Schedule auto-sync is disabled (SCHEDULE_SYNC_ENABLED=false)")
        return

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _sync_schedule_with_lock,
        trigger=IntervalTrigger(
            hours=settings.schedule_update_interval_hours,
            jitter=60,
        ),
        id="schedule_auto_sync",
        name="Schedule auto-sync",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.start()
    logger.info(
        "Schedule auto-sync scheduler started (interval=%dh)",
        settings.schedule_update_interval_hours,
    )


async def stop_scheduler() -> None:
    """Shutdown the scheduler and close the Redis connection."""
    global _scheduler, _redis

    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Schedule auto-sync scheduler stopped")

    if _redis is not None:
        await _redis.aclose()
        _redis = None
