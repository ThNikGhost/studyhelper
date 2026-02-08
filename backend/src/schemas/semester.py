"""Semester schemas."""

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SemesterBase(BaseModel):
    """Base semester schema."""

    number: int = Field(..., ge=1, le=12, description="Semester number (1-12)")
    year_start: int = Field(..., ge=2000, le=2100, description="Start year")
    year_end: int = Field(..., ge=2000, le=2100, description="End year")
    name: str = Field(..., min_length=1, max_length=100, description="Semester name")
    start_date: date | None = Field(None, description="Semester start date")
    end_date: date | None = Field(None, description="Semester end date")


class SemesterCreate(SemesterBase):
    """Schema for creating a semester."""

    @model_validator(mode="after")
    def validate_dates(self) -> "SemesterCreate":
        """Validate that start_date < end_date when both are set."""
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            msg = "start_date must be before end_date"
            raise ValueError(msg)
        return self


class SemesterUpdate(BaseModel):
    """Schema for updating a semester."""

    number: int | None = Field(None, ge=1, le=12)
    year_start: int | None = Field(None, ge=2000, le=2100)
    year_end: int | None = Field(None, ge=2000, le=2100)
    name: str | None = Field(None, min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "SemesterUpdate":
        """Validate that start_date < end_date when both are set."""
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            msg = "start_date must be before end_date"
            raise ValueError(msg)
        return self


class SemesterResponse(SemesterBase):
    """Schema for semester response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_current: bool
    created_at: datetime
    updated_at: datetime


# --- Timeline schemas ---


class TimelineDeadline(BaseModel):
    """A deadline event on the timeline."""

    work_id: int
    title: str
    work_type: str
    deadline: datetime
    subject_name: str
    subject_id: int
    status: str | None = None


class TimelineExam(BaseModel):
    """An exam event on the timeline."""

    schedule_entry_id: int
    subject_name: str
    lesson_date: date
    start_time: time
    end_time: time
    room: str | None = None
    teacher_name: str | None = None


class TimelineResponse(BaseModel):
    """Aggregated timeline data for a semester."""

    model_config = ConfigDict(from_attributes=True)

    semester: SemesterResponse
    deadlines: list[TimelineDeadline]
    exams: list[TimelineExam]
