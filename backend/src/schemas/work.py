"""Work schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class WorkType(str, Enum):
    """Type of academic work."""

    HOMEWORK = "homework"
    LAB = "lab"
    PRACTICE = "practice"
    COURSE_WORK = "course_work"
    REPORT = "report"
    TEST = "test"
    EXAM = "exam"
    OTHER = "other"


class WorkStatusEnum(str, Enum):
    """Status of work completion."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUBMITTED = "submitted"
    GRADED = "graded"


# Work schemas
class WorkBase(BaseModel):
    """Base work schema."""

    title: str = Field(..., min_length=1, max_length=300, description="Work title")
    description: str | None = Field(
        None, max_length=2000, description="Work description"
    )
    work_type: WorkType = Field(..., description="Type of work")
    deadline: datetime | None = Field(None, description="Deadline for the work")
    max_grade: int | None = Field(None, ge=0, description="Maximum possible grade")


class WorkCreate(WorkBase):
    """Schema for creating a work."""

    subject_id: int = Field(..., description="Subject ID")


class WorkUpdate(BaseModel):
    """Schema for updating a work."""

    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, max_length=2000)
    work_type: WorkType | None = Field(None)
    deadline: datetime | None = Field(None)
    max_grade: int | None = Field(None, ge=0)
    subject_id: int | None = Field(None)


class WorkResponse(WorkBase):
    """Schema for work response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    created_at: datetime
    updated_at: datetime


# WorkStatus schemas
class WorkStatusBase(BaseModel):
    """Base work status schema."""

    status: WorkStatusEnum = Field(
        default=WorkStatusEnum.NOT_STARTED, description="Current status"
    )
    grade: int | None = Field(None, ge=0, description="Received grade")
    notes: str | None = Field(None, max_length=2000, description="Personal notes")


class WorkStatusUpdate(BaseModel):
    """Schema for updating work status."""

    status: WorkStatusEnum | None = Field(None)
    grade: int | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=2000)


class WorkStatusResponse(WorkStatusBase):
    """Schema for work status response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    work_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# WorkStatusHistory schemas
class WorkStatusHistoryResponse(BaseModel):
    """Schema for work status history response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    work_status_id: int
    old_status: str | None
    new_status: str
    changed_at: datetime
    changed_by_id: int | None


# Combined response with status
class WorkWithStatusResponse(WorkResponse):
    """Work response with current user's status."""

    my_status: WorkStatusResponse | None = None


# Upcoming works
class UpcomingWorkResponse(BaseModel):
    """Schema for upcoming works with deadline."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    work_type: WorkType
    deadline: datetime
    subject_id: int
    subject_name: str
    my_status: WorkStatusEnum | None = None
