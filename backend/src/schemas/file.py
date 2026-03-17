"""Pydantic schemas for file uploads."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FileCategory(StrEnum):
    """Available file categories."""

    TEXTBOOK = "textbook"
    PROBLEM_SET = "problem_set"
    LECTURE = "lecture"
    LAB = "lab"
    CHEATSHEET = "cheatsheet"
    OTHER = "other"


class FileResponse(BaseModel):
    """Response schema for a single file."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    stored_filename: str
    mime_type: str
    size: int
    category: str
    subject_id: int | None
    subject_name: str | None = None
    work_id: int | None = None
    work_title: str | None = None
    uploaded_by: int
    created_at: datetime


class FileUpdateRequest(BaseModel):
    """Request schema for updating file metadata (category, filename, work attachment)."""

    category: FileCategory | None = None
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    work_id: int | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "FileUpdateRequest":
        """Ensure at least one valid field is provided in the request."""
        if not self.model_fields_set:
            raise ValueError("At least one field required")
        if "category" in self.model_fields_set and self.category is None:
            raise ValueError(
                "category cannot be null; omit the field to leave it unchanged"
            )
        if "filename" in self.model_fields_set and self.filename is None:
            raise ValueError(
                "filename cannot be null; omit the field to leave it unchanged"
            )
        return self


class FileListResponse(BaseModel):
    """Response schema for file list items."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    mime_type: str
    size: int
    category: str
    subject_id: int | None
    subject_name: str | None = None
    work_id: int | None = None
    work_title: str | None = None
    uploaded_by: int
    created_at: datetime
