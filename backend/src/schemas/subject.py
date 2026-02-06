"""Subject schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubjectBase(BaseModel):
    """Base subject schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Subject name")
    short_name: str | None = Field(
        None, max_length=50, description="Short name or abbreviation"
    )
    description: str | None = Field(
        None, max_length=2000, description="Subject description"
    )


class SubjectCreate(SubjectBase):
    """Schema for creating a subject."""

    semester_id: int = Field(..., description="Semester ID")


class SubjectUpdate(BaseModel):
    """Schema for updating a subject."""

    name: str | None = Field(None, min_length=1, max_length=200)
    short_name: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=2000)
    semester_id: int | None = Field(None)


class SubjectResponse(SubjectBase):
    """Schema for subject response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    semester_id: int
    created_at: datetime
    updated_at: datetime


# Note: SubjectWithSemesterResponse with embedded semester info
# can be added later if needed. Currently using SubjectResponse
# which includes semester_id.
