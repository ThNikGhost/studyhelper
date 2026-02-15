"""Telegram bot and dispatcher initialization."""

from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings

logger = logging.getLogger(__name__)

_bot: Bot | None = None
_dp: Dispatcher | None = None


def get_bot() -> Bot | None:
    """Get the bot instance (None if not initialized)."""
    return _bot


def get_dispatcher() -> Dispatcher | None:
    """Get the dispatcher instance (None if not initialized)."""
    return _dp


async def setup_bot() -> tuple[Bot, Dispatcher] | None:
    """Initialize bot and dispatcher.

    Returns None if TELEGRAM_BOT_TOKEN is not configured.
    """
    global _bot, _dp

    if not settings.telegram_bot_token:
        logger.info("Telegram bot disabled (TELEGRAM_BOT_TOKEN not set)")
        return None

    _bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    _dp = Dispatcher()

    # Register all handlers
    from src.telegram.handlers import register_all_handlers

    register_all_handlers(_dp)

    # Set webhook if URL is configured
    if settings.telegram_webhook_url:
        await _bot.set_webhook(
            url=settings.telegram_webhook_url,
            secret_token=settings.telegram_webhook_secret,
            drop_pending_updates=True,
        )
        logger.info("Telegram webhook set: %s", settings.telegram_webhook_url)

    bot_info = await _bot.me()
    logger.info("Telegram bot initialized: @%s", bot_info.username)
    return _bot, _dp


async def shutdown_bot() -> None:
    """Shutdown bot and remove webhook."""
    global _bot, _dp

    if _bot is not None:
        await _bot.delete_webhook(drop_pending_updates=True)
        await _bot.session.close()
        _bot = None
        logger.info("Telegram bot shut down")

    _dp = None
