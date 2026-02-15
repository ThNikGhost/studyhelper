"""Calendar feed schemas."""

from datetime import datetime

from pydantic import BaseModel


class CalendarFeedStatusResponse(BaseModel):
    """Calendar feed subscription status."""

    is_active: bool
    feed_url: str | None = None
    last_accessed_at: datetime | None = None
    created_at: datetime | None = None


class CalendarFeedCreateResponse(BaseModel):
    """Response after enabling calendar feed."""

    feed_url: str
