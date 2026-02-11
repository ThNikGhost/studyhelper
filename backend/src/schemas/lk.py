"""LK (личный кабинет) schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LkCredentialsCreate(BaseModel):
    """Schema for saving LK credentials."""

    email: str = Field(..., min_length=5, max_length=255, description="LK email")
    password: str = Field(..., min_length=1, max_length=255, description="LK password")


class LkStatusResponse(BaseModel):
    """Schema for LK status response."""

    has_credentials: bool
    last_sync_at: datetime | None


class SessionGradeResponse(BaseModel):
    """Schema for session grade response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_number: str
    subject_name: str
    result: str
    synced_at: datetime


class SemesterDisciplineResponse(BaseModel):
    """Schema for semester discipline response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    semester_number: int
    discipline_name: str
    control_form: str
    hours: int
    synced_at: datetime


class LkSyncResponse(BaseModel):
    """Schema for sync operation response."""

    grades_synced: int
    disciplines_synced: int
    last_sync_at: datetime


class LkStudentInfo(BaseModel):
    """Student info extracted from LK."""

    full_name: str | None = None
    group_name: str | None = None
    faculty: str | None = None
    course: int | None = None
    speciality: str | None = None
