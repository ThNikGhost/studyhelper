"""Attendance model — absences-only approach."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.schedule import ScheduleEntry
    from src.models.user import User


class Absence(Base):
    """Absence record — each row represents a missed lesson.

    Presence is implicit: no record = attended.
    """

    __tablename__ = "absences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    schedule_entry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schedule_entries.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    schedule_entry: Mapped["ScheduleEntry"] = relationship("ScheduleEntry")

    __table_args__ = (
        UniqueConstraint("user_id", "schedule_entry_id", name="uq_absence_user_entry"),
        Index("ix_absences_user_id", "user_id"),
        Index("ix_absences_schedule_entry_id", "schedule_entry_id"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Absence(id={self.id}, user_id={self.user_id}, "
            f"entry_id={self.schedule_entry_id})>"
        )
