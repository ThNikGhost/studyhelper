"""Pydantic schemas for file uploads."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


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
    uploaded_by: int
    created_at: datetime


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
    uploaded_by: int
    created_at: datetime
