"""Settings handlers: /notifications, /notify, /morning, callback queries."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.database import get_session_maker
from src.services import telegram as tg_service
from src.telegram.keyboards import notifications_keyboard

logger = logging.getLogger(__name__)
router = Router(name="settings")


@router.message(Command("notifications"))
async def cmd_notifications(message: Message) -> None:
    """Handle /notifications command — show settings with inline keyboard."""
    telegram_id = message.from_user.id  # type: ignore[union-attr]

    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)

    if not link:
        await message.answer(
            "\u274c Аккаунт не привязан.\n"
            "Используйте /start для инструкции."
        )
        return

    await message.answer(
        "\u2699\ufe0f <b>Настройки уведомлений</b>\n\n"
        "Нажмите кнопку для переключения:",
        reply_markup=notifications_keyboard(
            link.notify_deadlines,
            link.morning_summary,
        ),
    )


@router.message(Command("notify"))
async def cmd_notify(message: Message) -> None:
    """Handle /notify on/off command."""
    telegram_id = message.from_user.id  # type: ignore[union-attr]
    args = (message.text or "").split()

    if len(args) < 2 or args[1].lower() not in ("on", "off"):
        await message.answer(
            "Использование: /notify on или /notify off\n"
            "Включает/выключает уведомления о дедлайнах."
        )
        return

    enabled = args[1].lower() == "on"

    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)
        if not link:
            await message.answer(
                "\u274c Аккаунт не привязан.\n"
                "Используйте /start для инструкции."
            )
            return
        await tg_service.update_notifications(
            db, link.user_id, notify_deadlines=enabled
        )

    status = "\u2705 включены" if enabled else "\u274c выключены"
    await message.answer(f"Уведомления о дедлайнах {status}.")


@router.message(Command("morning"))
async def cmd_morning(message: Message) -> None:
    """Handle /morning on/off command."""
    telegram_id = message.from_user.id  # type: ignore[union-attr]
    args = (message.text or "").split()

    if len(args) < 2 or args[1].lower() not in ("on", "off"):
        await message.answer(
            "Использование: /morning on или /morning off\n"
            "Включает/выключает утреннюю сводку."
        )
        return

    enabled = args[1].lower() == "on"

    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)
        if not link:
            await message.answer(
                "\u274c Аккаунт не привязан.\n"
                "Используйте /start для инструкции."
            )
            return
        await tg_service.update_notifications(
            db, link.user_id, morning_summary=enabled
        )

    status = "\u2705 включена" if enabled else "\u274c выключена"
    await message.answer(f"Утренняя сводка {status}.")


@router.callback_query(F.data == "toggle_deadlines")
async def toggle_deadlines(callback: CallbackQuery) -> None:
    """Toggle deadline notifications via inline button."""
    telegram_id = callback.from_user.id

    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)
        if not link:
            await callback.answer("Аккаунт не привязан", show_alert=True)
            return

        new_value = not link.notify_deadlines
        await tg_service.update_notifications(
            db, link.user_id, notify_deadlines=new_value
        )

    # Refresh keyboard
    link.notify_deadlines = new_value
    await callback.message.edit_reply_markup(  # type: ignore[union-attr]
        reply_markup=notifications_keyboard(
            link.notify_deadlines,
            link.morning_summary,
        ),
    )
    status = "\u2705 вкл" if new_value else "\u274c выкл"
    await callback.answer(f"Дедлайны: {status}")


@router.callback_query(F.data == "toggle_morning")
async def toggle_morning(callback: CallbackQuery) -> None:
    """Toggle morning summary via inline button."""
    telegram_id = callback.from_user.id

    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)
        if not link:
            await callback.answer("Аккаунт не привязан", show_alert=True)
            return

        new_value = not link.morning_summary
        await tg_service.update_notifications(
            db, link.user_id, morning_summary=new_value
        )

    link.morning_summary = new_value
    await callback.message.edit_reply_markup(  # type: ignore[union-attr]
        reply_markup=notifications_keyboard(
            link.notify_deadlines,
            link.morning_summary,
        ),
    )
    status = "\u2705 вкл" if new_value else "\u274c выкл"
    await callback.answer(f"Утренняя сводка: {status}")
