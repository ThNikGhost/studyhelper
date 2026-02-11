"""Attendance model — absences-only approach."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.schedule import ScheduleEntry
    from src.models.user import User


class Absence(Base):
    """Absence record — each row represents a missed lesson.

    Presence is implicit: no record = attended.
    The subject_name and lesson_date fields preserve the absence identity
    even when schedule_entry_id is set to NULL by schedule re-sync.
    """

    __tablename__ = "absences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    schedule_entry_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("schedule_entries.id", ondelete="SET NULL"),
        nullable=True,
    )
    subject_name: Mapped[str] = mapped_column(String(200), nullable=False)
    lesson_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    schedule_entry: Mapped["ScheduleEntry | None"] = relationship("ScheduleEntry")

    __table_args__ = (
        UniqueConstraint("user_id", "schedule_entry_id", name="uq_absence_user_entry"),
        Index("ix_absences_user_id", "user_id"),
        Index("ix_absences_schedule_entry_id", "schedule_entry_id"),
        Index(
            "ix_absences_user_subject_date", "user_id", "subject_name", "lesson_date"
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Absence(id={self.id}, user_id={self.user_id}, "
            f"subject={self.subject_name}, entry_id={self.schedule_entry_id})>"
        )
