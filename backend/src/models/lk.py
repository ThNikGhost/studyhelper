"""LK (личный кабинет) models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class LkCredentials(Base, TimestampMixin):
    """Encrypted credentials for LK authentication.

    Stores user's LK email and password encrypted with Fernet.
    One credential set per user.
    """

    __tablename__ = "lk_credentials"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    encrypted_email: Mapped[str] = mapped_column(Text)  # Fernet encrypted
    encrypted_password: Mapped[str] = mapped_column(Text)  # Fernet encrypted
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="lk_credentials")

    def __repr__(self) -> str:
        """String representation."""
        return f"<LkCredentials(user_id={self.user_id}, last_sync={self.last_sync_at})>"


class SessionGrade(Base):
    """Grade from session (exam/zachet result).

    Stores grades synced from LK for each user.
    Unique constraint ensures no duplicate grades.
    """

    __tablename__ = "session_grades"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "session_number", "subject_name", name="uq_session_grade"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    session_number: Mapped[str] = mapped_column(String(50))  # "5 2025/2026"
    subject_name: Mapped[str] = mapped_column(String(300))
    result: Mapped[str] = mapped_column(String(50))  # "Отлично", "Хорошо", "Зачтено"
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        """String representation."""
        return f"<SessionGrade({self.session_number}: {self.subject_name} = {self.result})>"


class SemesterDiscipline(Base):
    """Discipline from study plan.

    Stores curriculum disciplines synced from LK for each user.
    Unique constraint ensures no duplicate disciplines per semester.
    """

    __tablename__ = "semester_disciplines"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "semester_number",
            "discipline_name",
            name="uq_semester_discipline",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    semester_number: Mapped[int] = mapped_column(Integer)  # 1-11
    discipline_name: Mapped[str] = mapped_column(String(300))
    control_form: Mapped[str] = mapped_column(String(100))  # "Экзамен", "Зачет"
    hours: Mapped[int] = mapped_column(Integer)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<SemesterDiscipline(sem={self.semester_number}: {self.discipline_name})>"
        )
