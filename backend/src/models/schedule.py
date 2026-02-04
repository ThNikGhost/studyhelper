"""Schedule models."""

from datetime import date, time
from enum import Enum

from sqlalchemy import Date, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class LessonType(str, Enum):
    """Lesson type enum."""

    LECTURE = "lecture"
    PRACTICE = "practice"
    LAB = "lab"
    SEMINAR = "seminar"
    EXAM = "exam"
    CONSULTATION = "consultation"
    OTHER = "other"


class DayOfWeek(int, Enum):
    """Day of week enum (ISO 8601: Monday=1, Sunday=7)."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class ScheduleEntry(Base, TimestampMixin):
    """Schedule entry model for individual lessons."""

    __tablename__ = "schedule_entries"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Specific date of the lesson
    lesson_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    # Time and day
    day_of_week: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 1-7 (ISO: Monday=1)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Week type (for alternating schedules) - deprecated, use lesson_date
    week_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # "odd", "even", or null for both

    # Lesson info
    subject_name: Mapped[str] = mapped_column(String(200), nullable=False)
    lesson_type: Mapped[str] = mapped_column(String(20), nullable=False)
    teacher_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    room: Mapped[str | None] = mapped_column(String(50), nullable=True)
    building: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Group info
    group_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subgroup: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Link to subject (optional, if subject exists in our DB)
    subject_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    subject: Mapped["Subject | None"] = relationship("Subject")

    # Link to teacher (optional, if teacher exists in our DB)
    teacher_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    teacher: Mapped["Teacher | None"] = relationship("Teacher")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ScheduleEntry(id={self.id}, day={self.day_of_week}, "
            f"subject={self.subject_name})>"
        )


class ScheduleSnapshot(Base, TimestampMixin):
    """Schedule snapshot for tracking changes."""

    __tablename__ = "schedule_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON dump
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    entries_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        """String representation."""
        return f"<ScheduleSnapshot(id={self.id}, date={self.snapshot_date})>"


# Import at the end to avoid circular imports
from src.models.subject import Subject  # noqa: E402
from src.models.teacher import Teacher  # noqa: E402
