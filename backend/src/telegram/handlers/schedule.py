"""Schedule-related handlers: /today, /tomorrow, /next + reply-keyboard buttons."""

from __future__ import annotations

import logging
import zoneinfo
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.config import settings
from src.database import get_session_maker
from src.models.user import User
from src.services import telegram as tg_service
from src.services.user import get_user_by_id
from src.telegram.formatters import (
    format_current_lesson,
    format_today_schedule,
    format_tomorrow_schedule,
)
from src.telegram.keyboards import main_keyboard
from src.telegram.schedule_utils import (
    get_filtered_current_lesson,
    get_filtered_day_schedule,
)

logger = logging.getLogger(__name__)
router = Router(name="schedule")


async def _require_linked(message: Message) -> User | None:
    """Check if user is linked. Returns User object or sends error and returns None."""
    telegram_id = message.from_user.id  # type: ignore[union-attr]
    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)
    if not link:
        await message.answer(
            "\u274c Аккаунт не привязан.\nИспользуйте /start для инструкции."
        )
        return None

    # Load full User object
    async with session_maker() as db:
        user = await get_user_by_id(db, link.user_id)

    if user is None:
        await message.answer("\u274c Ошибка: пользователь не найден.")
        return None

    return user


@router.message(Command("today", "schedule"))
async def cmd_today(message: Message) -> None:
    """Handle /today and /schedule commands."""
    user = await _require_linked(message)
    if user is None:
        return

    session_maker = get_session_maker()
    async with session_maker() as db:
        day = await get_filtered_day_schedule(db, user)

    await message.answer(format_today_schedule(day), reply_markup=main_keyboard())


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message) -> None:
    """Handle /tomorrow command."""
    user = await _require_linked(message)
    if user is None:
        return

    tz = zoneinfo.ZoneInfo(settings.timezone)
    tomorrow = datetime.now(tz).date() + timedelta(days=1)

    session_maker = get_session_maker()
    async with session_maker() as db:
        day = await get_filtered_day_schedule(db, user, target_date=tomorrow)

    await message.answer(format_tomorrow_schedule(day), reply_markup=main_keyboard())


@router.message(Command("next"))
async def cmd_next(message: Message) -> None:
    """Handle /next command."""
    user = await _require_linked(message)
    if user is None:
        return

    session_maker = get_session_maker()
    async with session_maker() as db:
        data = await get_filtered_current_lesson(db, user)

    await message.answer(format_current_lesson(data), reply_markup=main_keyboard())


@router.message(F.text == "\U0001f4da Расписание на сегодня")
async def btn_today(message: Message) -> None:
    """Handle reply-keyboard button for today's schedule."""
    await cmd_today(message)


@router.message(F.text == "\u23ed Следующее занятие")
async def btn_next(message: Message) -> None:
    """Handle reply-keyboard button for next lesson."""
    await cmd_next(message)
