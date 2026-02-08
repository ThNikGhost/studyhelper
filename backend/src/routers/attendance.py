"""Attendance router — mark absences and view stats."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.attendance import (
    AbsenceCreate,
    AbsenceResponse,
    AttendanceEntryResponse,
    AttendanceStatsResponse,
    MarkPresentRequest,
    SubjectAttendanceStats,
)
from src.services import attendance as attendance_service

router = APIRouter()


@router.post(
    "/mark-absent",
    response_model=AbsenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def mark_absent(
    data: AbsenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AbsenceResponse:
    """Mark a lesson as absent.

    Args:
        data: Request body with schedule_entry_id.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        Created absence record.
    """
    try:
        absence = await attendance_service.mark_absent(
            db, current_user.id, data.schedule_entry_id
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            ) from e
        if "Already marked" in msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=msg
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=msg
        ) from e

    return AbsenceResponse.model_validate(absence)


@router.post("/mark-present", status_code=status.HTTP_204_NO_CONTENT)
async def mark_present(
    data: MarkPresentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Mark a lesson as present (remove absence record).

    Args:
        data: Request body with schedule_entry_id.
        db: Database session.
        current_user: Authenticated user.
    """
    deleted = await attendance_service.mark_present(
        db, current_user.id, data.schedule_entry_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence record not found",
        )


@router.get("/", response_model=list[AttendanceEntryResponse])
async def get_attendance_entries(
    subject_id: int | None = Query(None, description="Filter by subject ID"),
    date_from: date | None = Query(None, description="Start date"),
    date_to: date | None = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AttendanceEntryResponse]:
    """Get past schedule entries with attendance status.

    Args:
        subject_id: Optional filter by subject.
        date_from: Optional start date.
        date_to: Optional end date.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        List of entries with is_absent flag.
    """
    entries = await attendance_service.get_attendance_entries(
        db, current_user.id, subject_id, date_from, date_to
    )
    return [AttendanceEntryResponse(**e) for e in entries]


@router.get("/stats", response_model=AttendanceStatsResponse)
async def get_attendance_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttendanceStatsResponse:
    """Get overall attendance statistics with per-subject breakdown.

    Args:
        db: Database session.
        current_user: Authenticated user.

    Returns:
        Overall stats and per-subject list.
    """
    stats = await attendance_service.get_attendance_stats(db, current_user.id)
    return AttendanceStatsResponse(**stats)


@router.get("/stats/{subject_id}", response_model=SubjectAttendanceStats)
async def get_subject_attendance_stats(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectAttendanceStats:
    """Get attendance stats for a specific subject.

    Args:
        subject_id: Subject ID.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        Subject-specific attendance stats.
    """
    stats = await attendance_service.get_subject_attendance_stats(
        db, current_user.id, subject_id
    )
    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No schedule entries found for this subject",
        )
    return SubjectAttendanceStats(**stats)
