"""Start, link, unlink, and status handlers."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.database import get_session_maker
from src.services import telegram as tg_service
from src.telegram.keyboards import main_keyboard

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "\U0001f393 <b>StudyHelper Bot</b>\n\n"
        "Привет! Я помогу тебе быть в курсе расписания и дедлайнов.\n\n"
        "<b>Как привязать аккаунт:</b>\n"
        "1. Откройте Настройки в приложении StudyHelper\n"
        "2. В секции Telegram нажмите «Сгенерировать код»\n"
        "3. Отправьте мне: /link КОД\n\n"
        "<b>Команды:</b>\n"
        "/today — расписание на сегодня\n"
        "/tomorrow — расписание на завтра\n"
        "/next — следующее занятие\n"
        "/deadlines — ближайшие дедлайны\n"
        "/notifications — настройки уведомлений\n"
        "/status — статус привязки\n"
        "/unlink — отвязать аккаунт",
        reply_markup=main_keyboard(),
    )


@router.message(Command("link"))
async def cmd_link(message: Message) -> None:
    """Handle /link CODE command."""
    if not message.text or len(message.text.split()) < 2:
        await message.answer(
            "\u2753 Укажите код привязки.\n"
            "Пример: /link ABC123\n\n"
            "Код можно получить в настройках приложения StudyHelper."
        )
        return

    code = message.text.split()[1].strip().upper()
    telegram_id = message.from_user.id  # type: ignore[union-attr]
    username = message.from_user.username  # type: ignore[union-attr]

    session_maker = get_session_maker()
    async with session_maker() as db:
        # Check if this TG account is already linked
        existing = await tg_service.get_link_by_telegram_id(db, telegram_id)
        if existing:
            await message.answer(
                "\u2139\ufe0f Этот Telegram аккаунт уже привязан к другому пользователю.\n"
                "Сначала отвяжите его командой /unlink."
            )
            return

        link = await tg_service.get_link_by_code(db, code)
        if not link:
            await message.answer(
                "\u274c Код не найден или истёк.\n"
                "Сгенерируйте новый код в настройках приложения."
            )
            return

        await tg_service.complete_link(db, link, telegram_id, username)

    await message.answer(
        "\u2705 <b>Аккаунт привязан!</b>\n\n"
        "Теперь вы будете получать уведомления.\n"
        "Используйте /notifications для настройки.",
        reply_markup=main_keyboard(),
    )
    logger.info(
        "Telegram linked: tg_id=%d, user_id=%d",
        telegram_id,
        link.user_id,
    )


@router.message(Command("unlink"))
async def cmd_unlink(message: Message) -> None:
    """Handle /unlink command."""
    telegram_id = message.from_user.id  # type: ignore[union-attr]

    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)
        if not link:
            await message.answer(
                "\u2139\ufe0f Ваш Telegram аккаунт не привязан ни к одному пользователю."
            )
            return

        await tg_service.unlink(db, link.user_id)

    await message.answer(
        "\u2705 Аккаунт отвязан. Уведомления отключены.\n"
        "Для повторной привязки используйте /link."
    )
    logger.info("Telegram unlinked: tg_id=%d", telegram_id)


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    """Handle /status command."""
    telegram_id = message.from_user.id  # type: ignore[union-attr]

    session_maker = get_session_maker()
    async with session_maker() as db:
        link = await tg_service.get_link_by_telegram_id(db, telegram_id)

    if not link:
        await message.answer(
            "\u274c <b>Не привязан</b>\n\n"
            "Используйте /start для инструкции по привязке."
        )
        return

    dl_status = "\u2705" if link.notify_deadlines else "\u274c"
    ms_status = "\u2705" if link.morning_summary else "\u274c"
    linked_str = link.linked_at.strftime("%d.%m.%Y %H:%M") if link.linked_at else "—"
    await message.answer(
        f"\u2705 <b>Привязан</b>\n\n"
        f"\U0001f464 Пользователь #{link.user_id}\n"
        f"\U0001f4c5 Привязан: {linked_str}\n\n"
        f"<b>Уведомления:</b>\n"
        f"  {dl_status} Дедлайны\n"
        f"  {ms_status} Утренняя сводка"
    )
