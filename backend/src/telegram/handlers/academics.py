"""Academic handlers: /deadlines."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.database import get_session_maker
from src.services import telegram as tg_service
from src.services.user import get_user_by_id
from src.services.work import get_upcoming_works
from src.telegram.formatters import format_deadlines
from src.telegram.schedule_utils import filter_works_by_hidden_subjects
from src.utils.schedule_filters import resolve_hidden_subjects

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
            "\u274c Аккаунт не привязан.\nИспользуйте /start для инструкции."
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
        user = await get_user_by_id(db, user_id)
        works = await get_upcoming_works(db, user_id, limit=10)
        if user is not None:
            hidden_config = await resolve_hidden_subjects(db, user)
            works = filter_works_by_hidden_subjects(works, hidden_config)

    await message.answer(format_deadlines(works))
