"""Work models."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.subject import Subject
    from src.models.user import User


class WorkType(str, Enum):
    """Type of academic work."""

    HOMEWORK = "homework"  # Домашняя работа
    LAB = "lab"  # Лабораторная работа
    PRACTICE = "practice"  # Практическая работа
    COURSE_WORK = "course_work"  # Курсовая работа
    REPORT = "report"  # Реферат
    TEST = "test"  # Контрольная работа
    EXAM = "exam"  # Экзамен
    OTHER = "other"  # Другое


class WorkStatusEnum(str, Enum):
    """Status of work completion."""

    NOT_STARTED = "not_started"  # Не начато
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"  # Выполнено
    SUBMITTED = "submitted"  # Сдано
    GRADED = "graded"  # Оценено


class Work(Base, TimestampMixin):
    """Academic work model."""

    __tablename__ = "works"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    work_type: Mapped[str] = mapped_column(String(20), nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    max_grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="works")
    statuses: Mapped[list["WorkStatus"]] = relationship(
        "WorkStatus", back_populates="work", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Work(id={self.id}, title={self.title})>"


class WorkStatus(Base, TimestampMixin):
    """Work status for each user (pair mode)."""

    __tablename__ = "work_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    work_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=WorkStatusEnum.NOT_STARTED.value
    )
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    work: Mapped["Work"] = relationship("Work", back_populates="statuses")
    user: Mapped["User"] = relationship("User", back_populates="work_statuses")
    history: Mapped[list["WorkStatusHistory"]] = relationship(
        "WorkStatusHistory", back_populates="work_status", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<WorkStatus(id={self.id}, work_id={self.work_id}, user_id={self.user_id}, status={self.status})>"


class WorkStatusHistory(Base):
    """History of status changes for audit trail."""

    __tablename__ = "work_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    work_status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("work_statuses.id", ondelete="CASCADE"), nullable=False
    )
    old_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    changed_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    work_status: Mapped["WorkStatus"] = relationship(
        "WorkStatus", back_populates="history"
    )
    changed_by: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        """String representation."""
        return f"<WorkStatusHistory(id={self.id}, old={self.old_status}, new={self.new_status})>"
