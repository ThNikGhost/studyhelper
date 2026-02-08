"""Pydantic schemas for lesson notes."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class LessonNoteCreate(BaseModel):
    """Schema for creating a lesson note."""

    schedule_entry_id: int | None = None
    subject_name: str = Field(max_length=200)
    lesson_date: date | None = None
    content: str = Field(min_length=1, max_length=2000)


class LessonNoteUpdate(BaseModel):
    """Schema for updating a lesson note."""

    content: str = Field(min_length=1, max_length=2000)


class LessonNoteResponse(BaseModel):
    """Response schema for a lesson note."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    schedule_entry_id: int | None
    subject_name: str
    lesson_date: date | None
    content: str
    created_at: datetime
    updated_at: datetime
