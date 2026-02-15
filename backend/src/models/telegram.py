"""Telegram bot link model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class TelegramLink(Base, TimestampMixin):
    """Telegram account link for a user.

    Stores the connection between a StudyHelper user and their
    Telegram account. One link per user (uselist=False).
    """

    __tablename__ = "telegram_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, nullable=True, index=True
    )
    telegram_username: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    link_code: Mapped[str | None] = mapped_column(
        String(6), nullable=True, index=True
    )
    link_code_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notify_deadlines: Mapped[bool] = mapped_column(Boolean, default=True)
    morning_summary: Mapped[bool] = mapped_column(Boolean, default=True)
    linked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="telegram_link")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<TelegramLink(user_id={self.user_id}, "
            f"telegram_id={self.telegram_id})>"
        )
