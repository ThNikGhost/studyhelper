"""Teacher model."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class Teacher(Base, TimestampMixin):
    """Teacher model for storing information about professors."""

    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str | None] = mapped_column(String(200), nullable=True)
    position: Mapped[str | None] = mapped_column(String(200), nullable=True)
    office: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Teacher(id={self.id}, full_name={self.full_name})>"
