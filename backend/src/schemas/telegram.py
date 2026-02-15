"""Telegram bot schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelegramStatusResponse(BaseModel):
    """Telegram link status for the current user."""

    is_linked: bool
    telegram_username: str | None = None
    notify_deadlines: bool = True
    morning_summary: bool = True
    link_code: str | None = None
    link_code_expires_at: datetime | None = None


class TelegramLinkCodeResponse(BaseModel):
    """Response with a generated link code."""

    link_code: str
    expires_at: datetime
    bot_username: str


class TelegramNotificationsUpdate(BaseModel):
    """Update notification preferences."""

    notify_deadlines: bool | None = Field(None, description="Toggle deadline alerts")
    morning_summary: bool | None = Field(None, description="Toggle morning summary")


class TelegramLinkResponse(BaseModel):
    """Full telegram link response (admin/internal)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    telegram_id: int | None
    telegram_username: str | None
    notify_deadlines: bool
    morning_summary: bool
    linked_at: datetime | None
    created_at: datetime
    updated_at: datetime
