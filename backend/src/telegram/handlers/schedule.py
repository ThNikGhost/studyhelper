"""Schedule-related handlers: /today, /tomorrow, /week, /next."""

from __future__ import annotations

import logging
import zoneinfo
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.config import settings
from src.database import get_session_maker
from src.services import telegram as tg_service
from src.services.schedule import (
    get_current_lesson,
    get_today_schedule,
    get_week_schedule,
)
from src.telegram.formatters import (
    format_current_lesson,
    format_today_schedule,
    format_tomorrow_schedule,
    format_week_schedule,
)

logger = logging.getLogger(__name__)
router = Router(name="schedule")


async def _require_linked(message: Message) -> int | None:
    """Check if user is linked. Returns user_id or sends error and returns None."""
    telegram_id = message.from_user.id  # type: ignore[union-attr]
    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)
    if not link:
        await message.answer(
            "\u274c Аккаунт не привязан.\n"
            "Используйте /start для инструкции."
        )
        return None
    return link.user_id


@router.message(Command("today", "schedule"))
async def cmd_today(message: Message) -> None:
    """Handle /today and /schedule commands."""
    user_id = await _require_linked(message)
    if user_id is None:
        return

    session_maker = get_session_maker()
    async with session_maker() as db:
        day = await get_today_schedule(db)

    await message.answer(format_today_schedule(day))


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message) -> None:
    """Handle /tomorrow command."""
    user_id = await _require_linked(message)
    if user_id is None:
        return

    tz = zoneinfo.ZoneInfo(settings.timezone)
    tomorrow = datetime.now(tz).date() + timedelta(days=1)

    session_maker = get_session_maker()
    async with session_maker() as db:
        day = await get_today_schedule(db, target_date=tomorrow)

    await message.answer(format_tomorrow_schedule(day))


@router.message(Command("week"))
async def cmd_week(message: Message) -> None:
    """Handle /week command."""
    user_id = await _require_linked(message)
    if user_id is None:
        return

    session_maker = get_session_maker()
    async with session_maker() as db:
        week = await get_week_schedule(db)

    text = format_week_schedule(week)
    # Telegram message limit is 4096 chars
    if len(text) > 4096:
        # Split by days
        parts = text.split("\n\n\U0001f4c5")
        current = parts[0]
        for part in parts[1:]:
            chunk = "\U0001f4c5" + part
            if len(current) + len(chunk) + 2 > 4000:
                await message.answer(current)
                current = chunk
            else:
                current += "\n\n" + chunk
        if current:
            await message.answer(current)
    else:
        await message.answer(text)


@router.message(Command("next"))
async def cmd_next(message: Message) -> None:
    """Handle /next command."""
    user_id = await _require_linked(message)
    if user_id is None:
        return

    session_maker = get_session_maker()
    async with session_maker() as db:
        data = await get_current_lesson(db)

    await message.answer(format_current_lesson(data))
