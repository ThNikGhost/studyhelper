"""Semester model."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.subject import Subject


class Semester(Base, TimestampMixin):
    """Semester model for organizing subjects by academic periods."""

    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    year_start: Mapped[int] = mapped_column(Integer, nullable=False)
    year_end: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject", back_populates="semester", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Semester(id={self.id}, name={self.name}, is_current={self.is_current})>"
        )
