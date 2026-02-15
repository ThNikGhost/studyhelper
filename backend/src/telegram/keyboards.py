"""Inline keyboards for Telegram bot."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_keyboard() -> ReplyKeyboardMarkup:
    """Persistent reply keyboard with main actions."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="\U0001f4da Расписание на сегодня"),
                KeyboardButton(text="\u23ed Следующее занятие"),
            ],
        ],
        resize_keyboard=True,
    )


def notifications_keyboard(
    notify_deadlines: bool,
    morning_summary: bool,
) -> InlineKeyboardMarkup:
    """Build notification settings keyboard."""
    dl_status = "\u2705" if notify_deadlines else "\u274c"
    ms_status = "\u2705" if morning_summary else "\u274c"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{dl_status} Дедлайны",
                    callback_data="toggle_deadlines",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{ms_status} Утренняя сводка",
                    callback_data="toggle_morning",
                ),
            ],
        ]
    )
