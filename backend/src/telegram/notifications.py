"""Notification sender for Telegram bot."""

from __future__ import annotations

import logging

from src.database import get_session_maker
from src.services import telegram as tg_service
from src.telegram.formatters import (
    format_deadline_alert,
    format_morning_summary,
    format_schedule_changed,
)

logger = logging.getLogger(__name__)


async def send_schedule_changed() -> int:
    """Notify all linked users about schedule changes.

    Returns:
        Number of users notified.
    """
    from src.telegram.bot import get_bot

    bot = get_bot()
    if bot is None:
        return 0

    session_maker = get_session_maker()
    async with session_maker() as db:
        links = await tg_service.get_all_linked_users(db)

    text = format_schedule_changed()
    sent = 0
    for link in links:
        try:
            await bot.send_message(link.telegram_id, text)  # type: ignore[arg-type]
            sent += 1
        except Exception:
            logger.warning(
                "Failed to send schedule change to tg_id=%s",
                link.telegram_id,
            )
    logger.info("Schedule change notification sent to %d/%d users", sent, len(links))
    return sent


async def send_morning_summaries() -> int:
    """Send morning summary to all subscribed users.

    Returns:
        Number of users notified.
    """
    from src.telegram.bot import get_bot

    bot = get_bot()
    if bot is None:
        return 0

    session_maker = get_session_maker()
    async with session_maker() as db:
        links = await tg_service.get_users_with_morning_summary(db)

    if not links:
        return 0

    from src.services.schedule import get_today_schedule
    from src.services.work import get_upcoming_works

    sent = 0
    for link in links:
        try:
            async with session_maker() as db:
                day = await get_today_schedule(db)
                works = await get_upcoming_works(db, link.user_id, limit=3)

            text = format_morning_summary(day, works)
            await bot.send_message(link.telegram_id, text)  # type: ignore[arg-type]
            sent += 1
        except Exception:
            logger.warning(
                "Failed to send morning summary to tg_id=%s",
                link.telegram_id,
            )

    logger.info("Morning summary sent to %d/%d users", sent, len(links))
    return sent


async def send_deadline_alerts() -> int:
    """Check and send deadline alerts to subscribed users.

    Sends alerts for works with deadlines in the next 24 hours.

    Returns:
        Number of alerts sent.
    """
    from datetime import UTC, datetime, timedelta

    from src.telegram.bot import get_bot

    bot = get_bot()
    if bot is None:
        return 0

    session_maker = get_session_maker()
    async with session_maker() as db:
        links = await tg_service.get_users_with_deadline_alerts(db)

    if not links:
        return 0

    from src.services.work import get_upcoming_works

    now = datetime.now(UTC)
    sent = 0
    for link in links:
        try:
            async with session_maker() as db:
                works = await get_upcoming_works(db, link.user_id, limit=20)

            # Filter works with deadline within 24 hours
            urgent = [
                w
                for w in works
                if w.deadline and w.deadline - now <= timedelta(hours=24)
            ]
            for w in urgent:
                text = format_deadline_alert(w)
                await bot.send_message(link.telegram_id, text)  # type: ignore[arg-type]
                sent += 1
        except Exception:
            logger.warning(
                "Failed to send deadline alert to tg_id=%s",
                link.telegram_id,
            )

    logger.info("Deadline alerts sent: %d total", sent)
    return sent
