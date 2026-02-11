"""Lesson note model — user notes for schedule entries."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.schedule import ScheduleEntry
    from src.models.user import User


class LessonNote(Base, TimestampMixin):
    """User note for a subject.

    Each user can have at most one note per subject (by subject_name).
    The schedule_entry_id and lesson_date are informational,
    tracking the last entry where the note was edited.
    """

    __tablename__ = "lesson_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    schedule_entry_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("schedule_entries.id", ondelete="CASCADE"),
        nullable=True,
    )
    subject_name: Mapped[str] = mapped_column(String(200), nullable=False)
    lesson_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User")
    schedule_entry: Mapped["ScheduleEntry | None"] = relationship("ScheduleEntry")

    __table_args__ = (
        UniqueConstraint("user_id", "subject_name", name="uq_lesson_note_user_subject"),
        Index("ix_lesson_notes_user_date", "user_id", "lesson_date"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<LessonNote(id={self.id}, user_id={self.user_id}, "
            f"subject={self.subject_name})>"
        )
