"""Classmate models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class Classmate(Base, TimestampMixin):
    """Classmate model storing shared basic information."""

    __tablename__ = "classmates"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    group_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subgroup: Mapped[int | None] = mapped_column(nullable=True)

    details: Mapped[list[ClassmateDetail]] = relationship(
        "ClassmateDetail",
        back_populates="classmate",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Classmate(id={self.id}, full_name={self.full_name})>"


class ClassmateDetail(Base, TimestampMixin):
    """Per-user classmate details (contacts and notes visible only to the owner)."""

    __tablename__ = "classmate_details"
    __table_args__ = (
        UniqueConstraint(
            "classmate_id", "user_id", name="uq_classmate_details_classmate_user"
        ),
        Index("ix_classmate_details_classmate_id", "classmate_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    classmate_id: Mapped[int] = mapped_column(
        ForeignKey("classmates.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telegram: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vk: Mapped[str | None] = mapped_column(String(200), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    classmate: Mapped[Classmate] = relationship("Classmate", back_populates="details")

    def __repr__(self) -> str:
        """String representation."""
        return f"<ClassmateDetail(classmate_id={self.classmate_id}, user_id={self.user_id})>"
