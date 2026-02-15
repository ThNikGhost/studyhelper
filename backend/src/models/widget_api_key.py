"""Widget API key model for phone widget authentication."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class WidgetApiKey(Base, TimestampMixin):
    """Widget API key for a user.

    Stores a per-user secret token used for phone widget authentication.
    Widget apps (Scriptable, HTTP Shortcuts) use this token as a query
    parameter to fetch the next lesson data.
    """

    __tablename__ = "widget_api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="widget_api_key")

    def __repr__(self) -> str:
        """String representation."""
        return f"<WidgetApiKey(user_id={self.user_id}, token={self.token[:8]}...)>"
