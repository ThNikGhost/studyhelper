"""Calendar feed model for iCal subscriptions."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class CalendarFeed(Base, TimestampMixin):
    """Calendar feed subscription for a user.

    Stores a per-user secret token used to generate a public .ics URL.
    Calendar clients (Google Calendar, Apple Calendar, Outlook) subscribe
    to this URL and refresh automatically.
    """

    __tablename__ = "calendar_feeds"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="calendar_feed")

    def __repr__(self) -> str:
        """String representation."""
        return f"<CalendarFeed(user_id={self.user_id}, token={self.token[:8]}...)>"
