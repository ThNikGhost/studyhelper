"""Academic handlers: /deadlines, /grades, /attendance."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.database import get_session_maker
from src.services import telegram as tg_service
from src.services.lk import get_grades
from src.services.work import get_upcoming_works
from src.telegram.formatters import format_attendance, format_deadlines, format_grades

logger = logging.getLogger(__name__)
router = Router(name="academics")


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


@router.message(Command("deadlines"))
async def cmd_deadlines(message: Message) -> None:
    """Handle /deadlines command."""
    user_id = await _require_linked(message)
    if user_id is None:
        return

    session_maker = get_session_maker()
    async with session_maker() as db:
        works = await get_upcoming_works(db, user_id, limit=10)

    await message.answer(format_deadlines(works))


@router.message(Command("grades"))
async def cmd_grades(message: Message) -> None:
    """Handle /grades command."""
    user_id = await _require_linked(message)
    if user_id is None:
        return

    session_maker = get_session_maker()
    async with session_maker() as db:
        grades = await get_grades(db, user_id)

    await message.answer(format_grades(grades))


@router.message(Command("attendance"))
async def cmd_attendance(message: Message) -> None:
    """Handle /attendance command."""
    user_id = await _require_linked(message)
    if user_id is None:
        return

    session_maker = get_session_maker()
    async with session_maker() as db:
        # Find current semester
        from sqlalchemy import select

        from src.models.semester import Semester

        result = await db.execute(
            select(Semester)
            .where(Semester.is_current.is_(True))
            .limit(1)
        )
        semester = result.scalar_one_or_none()
        if not semester:
            await message.answer(
                "\u2139\ufe0f Текущий семестр не найден.\n"
                "Данные о посещаемости недоступны."
            )
            return

        from src.services.attendance import get_attendance_stats

        stats = await get_attendance_stats(db, user_id, semester.id)

    await message.answer(format_attendance(stats))
