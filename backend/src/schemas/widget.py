"""Widget API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WidgetApiKeyStatusResponse(BaseModel):
    """Widget API key status response."""

    model_config = ConfigDict(from_attributes=True)

    is_active: bool
    api_key: str | None = None
    widget_url: str | None = None
    last_used_at: datetime | None = None
    created_at: datetime | None = None


class WidgetApiKeyCreateResponse(BaseModel):
    """Response after enabling widget API key."""

    api_key: str
    widget_url: str


class NextLessonResponse(BaseModel):
    """Next lesson data for phone widgets."""

    subject: str | None = None
    time_start: str | None = None
    time_end: str | None = None
    location: str | None = None
    teacher: str | None = None
    minutes_until: int | None = None
    lesson_type: str | None = None
    is_today: bool = False
    no_more_lessons: bool = False
    cached_at: str | None = None
