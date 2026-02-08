"""File model for uploaded study materials."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.subject import Subject
    from src.models.user import User


class File(Base):
    """Uploaded file model — immutable after creation."""

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="SET NULL"),
        nullable=True,
    )
    uploaded_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    subject: Mapped["Subject | None"] = relationship("Subject")
    uploader: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_files_subject_id", "subject_id"),
        Index("ix_files_category", "category"),
        Index("ix_files_uploaded_by", "uploaded_by"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<File(id={self.id}, filename={self.filename}, category={self.category})>"
        )
