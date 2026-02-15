"""Telegram bot router.

Webhook endpoint + REST API for link management.
"""

from __future__ import annotations

import logging

from aiogram.types import Update
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.telegram import (
    TelegramLinkCodeResponse,
    TelegramNotificationsUpdate,
    TelegramStatusResponse,
)
from src.services import telegram as tg_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook", include_in_schema=False)
async def telegram_webhook(request: Request) -> dict[str, str]:
    """Handle incoming Telegram webhook updates.

    Validates the secret token header before processing.
    """
    # Validate secret header
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if settings.telegram_webhook_secret and secret != settings.telegram_webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid secret")

    from src.telegram.bot import get_bot, get_dispatcher

    bot = get_bot()
    dp = get_dispatcher()
    if bot is None or dp is None:
        raise HTTPException(status_code=503, detail="Telegram bot not initialized")

    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"status": "ok"}


@router.get("/status", response_model=TelegramStatusResponse)
async def get_telegram_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TelegramStatusResponse:
    """Get Telegram link status for current user."""
    link = await tg_service.get_link_by_user(db, current_user.id)
    if link is None:
        return TelegramStatusResponse(is_linked=False)

    return TelegramStatusResponse(
        is_linked=link.telegram_id is not None,
        telegram_username=link.telegram_username,
        notify_deadlines=link.notify_deadlines,
        morning_summary=link.morning_summary,
        link_code=link.link_code,
        link_code_expires_at=link.link_code_expires_at,
    )


@router.post("/link-code", response_model=TelegramLinkCodeResponse)
async def generate_link_code(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TelegramLinkCodeResponse:
    """Generate a 6-digit link code for the current user.

    The code expires in 10 minutes.
    """
    link = await tg_service.generate_link_code(db, current_user.id)

    # Determine bot username
    from src.telegram.bot import get_bot

    bot = get_bot()
    bot_username = ""
    if bot:
        bot_info = await bot.me()
        bot_username = bot_info.username or ""

    return TelegramLinkCodeResponse(
        link_code=link.link_code,  # type: ignore[arg-type]
        expires_at=link.link_code_expires_at,  # type: ignore[arg-type]
        bot_username=bot_username,
    )


@router.delete("/link", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_telegram(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Unlink Telegram account from current user."""
    removed = await tg_service.unlink(db, current_user.id)
    if not removed:
        raise HTTPException(
            status_code=404,
            detail="No Telegram link found",
        )


@router.patch("/notifications", response_model=TelegramStatusResponse)
async def update_notifications(
    data: TelegramNotificationsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TelegramStatusResponse:
    """Update notification preferences for current user."""
    link = await tg_service.update_notifications(
        db,
        current_user.id,
        notify_deadlines=data.notify_deadlines,
        morning_summary=data.morning_summary,
    )
    if link is None:
        raise HTTPException(
            status_code=404,
            detail="No Telegram link found",
        )

    return TelegramStatusResponse(
        is_linked=link.telegram_id is not None,
        telegram_username=link.telegram_username,
        notify_deadlines=link.notify_deadlines,
        morning_summary=link.morning_summary,
    )
