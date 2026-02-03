"""Schedule schemas."""

from datetime import date, datetime, time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class LessonType(str, Enum):
    """Lesson type enum."""

    LECTURE = "lecture"
    PRACTICE = "practice"
    LAB = "lab"
    SEMINAR = "seminar"
    EXAM = "exam"
    CONSULTATION = "consultation"
    OTHER = "other"


class DayOfWeek(int, Enum):
    """Day of week enum (ISO 8601: Monday=1, Sunday=7)."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class WeekType(str, Enum):
    """Week type for alternating schedules."""

    ODD = "odd"
    EVEN = "even"


# Schedule Entry schemas
class ScheduleEntryBase(BaseModel):
    """Base schedule entry schema."""

    day_of_week: DayOfWeek = Field(..., description="Day of week (1=Monday, 7=Sunday)")
    start_time: time = Field(..., description="Lesson start time")
    end_time: time = Field(..., description="Lesson end time")
    week_type: WeekType | None = Field(
        None, description="Week type (odd/even) or null for both"
    )
    subject_name: str = Field(..., min_length=1, max_length=200, description="Subject")
    lesson_type: LessonType = Field(..., description="Type of lesson")
    teacher_name: str | None = Field(None, max_length=200, description="Teacher name")
    room: str | None = Field(None, max_length=50, description="Room number")
    building: str | None = Field(None, max_length=100, description="Building name")
    group_name: str | None = Field(None, max_length=50, description="Group name")
    subgroup: int | None = Field(None, ge=1, le=10, description="Subgroup number")
    notes: str | None = Field(None, description="Additional notes")
    subject_id: int | None = Field(None, description="Link to Subject model")
    teacher_id: int | None = Field(None, description="Link to Teacher model")


class ScheduleEntryCreate(ScheduleEntryBase):
    """Schema for creating a schedule entry."""

    pass


class ScheduleEntryUpdate(BaseModel):
    """Schema for updating a schedule entry."""

    day_of_week: DayOfWeek | None = Field(None)
    start_time: time | None = Field(None)
    end_time: time | None = Field(None)
    week_type: WeekType | None = Field(None)
    subject_name: str | None = Field(None, min_length=1, max_length=200)
    lesson_type: LessonType | None = Field(None)
    teacher_name: str | None = Field(None, max_length=200)
    room: str | None = Field(None, max_length=50)
    building: str | None = Field(None, max_length=100)
    group_name: str | None = Field(None, max_length=50)
    subgroup: int | None = Field(None, ge=1, le=10)
    notes: str | None = Field(None)
    subject_id: int | None = Field(None)
    teacher_id: int | None = Field(None)


class ScheduleEntryResponse(ScheduleEntryBase):
    """Schema for schedule entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Schedule Snapshot schemas
class ScheduleSnapshotBase(BaseModel):
    """Base schedule snapshot schema."""

    snapshot_date: date = Field(..., description="Date of snapshot")
    content_hash: str = Field(..., max_length=64, description="SHA-256 hash")
    raw_data: str | None = Field(None, description="Raw JSON data")
    source_url: str | None = Field(None, max_length=500, description="Source URL")
    entries_count: int = Field(0, ge=0, description="Number of entries")


class ScheduleSnapshotCreate(ScheduleSnapshotBase):
    """Schema for creating a schedule snapshot."""

    pass


class ScheduleSnapshotResponse(ScheduleSnapshotBase):
    """Schema for schedule snapshot response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Additional response schemas
class DayScheduleResponse(BaseModel):
    """Schedule for a specific day."""

    date: date
    day_of_week: DayOfWeek
    day_name: str
    entries: list[ScheduleEntryResponse]


class WeekScheduleResponse(BaseModel):
    """Schedule for a week."""

    week_start: date
    week_end: date
    week_number: int
    is_odd_week: bool
    days: list[DayScheduleResponse]


class CurrentLessonResponse(BaseModel):
    """Current or next lesson response."""

    current: ScheduleEntryResponse | None = Field(
        None, description="Currently ongoing lesson"
    )
    next: ScheduleEntryResponse | None = Field(None, description="Next upcoming lesson")
    time_until_next: int | None = Field(
        None, description="Minutes until next lesson starts"
    )
