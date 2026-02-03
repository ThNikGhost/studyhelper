"""Semester schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SemesterBase(BaseModel):
    """Base semester schema."""

    number: int = Field(..., ge=1, le=12, description="Semester number (1-12)")
    year_start: int = Field(..., ge=2000, le=2100, description="Start year")
    year_end: int = Field(..., ge=2000, le=2100, description="End year")
    name: str = Field(..., min_length=1, max_length=100, description="Semester name")


class SemesterCreate(SemesterBase):
    """Schema for creating a semester."""

    pass


class SemesterUpdate(BaseModel):
    """Schema for updating a semester."""

    number: int | None = Field(None, ge=1, le=12)
    year_start: int | None = Field(None, ge=2000, le=2100)
    year_end: int | None = Field(None, ge=2000, le=2100)
    name: str | None = Field(None, min_length=1, max_length=100)


class SemesterResponse(SemesterBase):
    """Schema for semester response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_current: bool
    created_at: datetime
    updated_at: datetime
