"""APScheduler jobs for Telegram notifications."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import settings

logger = logging.getLogger(__name__)


async def _job_morning_summary() -> None:
    """APScheduler job: send morning summaries (with Redis lock)."""
    from src.telegram.notifications import send_morning_summaries_locked

    await send_morning_summaries_locked()


async def _job_deadline_check() -> None:
    """APScheduler job: check and send deadline alerts (with Redis lock)."""
    from src.telegram.notifications import send_deadline_alerts_locked

    await send_deadline_alerts_locked()


def register_telegram_jobs(scheduler: AsyncIOScheduler) -> None:
    """Register Telegram notification jobs with the scheduler.

    Args:
        scheduler: The APScheduler instance.
    """
    tz = settings.timezone

    # Morning summary at 7:30 local time
    scheduler.add_job(
        _job_morning_summary,
        trigger=CronTrigger(hour=7, minute=30, timezone=tz),
        id="telegram_morning_summary",
        name="Telegram morning summary",
        replace_existing=True,
        misfire_grace_time=1800,
    )

    # Deadline check twice a day at 8:00 and 20:00
    scheduler.add_job(
        _job_deadline_check,
        trigger=CronTrigger(hour="8,20", minute=0, timezone=tz),
        id="telegram_deadline_check",
        name="Telegram deadline check",
        replace_existing=True,
        misfire_grace_time=1800,
    )

    logger.info("Telegram notification jobs registered")
