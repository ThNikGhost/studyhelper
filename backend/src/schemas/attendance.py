"""Pydantic schemas for attendance (absences)."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class AbsenceCreate(BaseModel):
    """Schema for marking a lesson as absent."""

    schedule_entry_id: int


class AbsenceResponse(BaseModel):
    """Response schema for an absence record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    schedule_entry_id: int | None
    subject_name: str
    lesson_date: date | None = None
    created_at: datetime


class MarkPresentRequest(BaseModel):
    """Schema for marking a lesson as present (removing absence)."""

    schedule_entry_id: int


class AttendanceEntryResponse(BaseModel):
    """Schedule entry augmented with attendance status."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    lesson_date: str | None
    subject_name: str
    lesson_type: str
    start_time: str
    end_time: str
    teacher_name: str | None
    room: str | None
    subject_id: int | None
    is_absent: bool
    absence_id: int | None = None


class SubjectAttendanceStats(BaseModel):
    """Attendance stats for a single subject."""

    subject_name: str
    subject_id: int | None = None
    planned_classes: int = 0  # From Subject.planned_classes
    total_classes: int  # Completed lessons count
    absences: int
    attended: int
    attendance_percent: float


class AttendanceStatsResponse(BaseModel):
    """Overall attendance statistics."""

    total_planned: int = 0  # Sum of Subject.planned_classes
    total_completed: int = 0  # Completed lessons count
    total_classes: int  # Backwards compat (= total_completed)
    absences: int
    attended: int
    attendance_percent: float
    by_subject: list[SubjectAttendanceStats]
