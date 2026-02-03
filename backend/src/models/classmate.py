"""Classmate model."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class Classmate(Base, TimestampMixin):
    """Classmate model for storing information about classmates."""

    __tablename__ = "classmates"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telegram: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vk: Mapped[str | None] = mapped_column(String(200), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    group_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subgroup: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Classmate(id={self.id}, full_name={self.full_name})>"
