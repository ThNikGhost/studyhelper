"""Subject model."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.semester import Semester


class Subject(Base, TimestampMixin):
    """Subject model for academic courses."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    semester_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    semester: Mapped["Semester"] = relationship("Semester", back_populates="subjects")

    # Works relationship will be added when Work model is created
    # works: Mapped[list["Work"]] = relationship(
    #     "Work", back_populates="subject", cascade="all, delete-orphan"
    # )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Subject(id={self.id}, name={self.name})>"
