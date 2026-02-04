"""Schedule router."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.schedule import (
    CurrentLessonResponse,
    DayScheduleResponse,
    ScheduleEntryCreate,
    ScheduleEntryResponse,
    ScheduleEntryUpdate,
    ScheduleSnapshotResponse,
    WeekScheduleResponse,
)
from src.services import schedule as schedule_service

router = APIRouter()


# High-level schedule endpoints (most commonly used)
@router.get("/week", response_model=WeekScheduleResponse)
async def get_week_schedule(
    target_date: date | None = Query(None, description="Date within target week"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WeekScheduleResponse:
    """Get schedule for a week (defaults to current week)."""
    return await schedule_service.get_week_schedule(db, target_date)


@router.get("/today", response_model=DayScheduleResponse)
async def get_today_schedule(
    target_date: date | None = Query(
        None, description="Target date (defaults to today)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DayScheduleResponse:
    """Get schedule for today (or specified date)."""
    return await schedule_service.get_today_schedule(db, target_date)


@router.get("/current", response_model=CurrentLessonResponse)
async def get_current_lesson(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CurrentLessonResponse:
    """Get current and next upcoming lesson."""
    return await schedule_service.get_current_lesson(db)


# CRUD endpoints for schedule entries
@router.get("/entries", response_model=list[ScheduleEntryResponse])
async def get_schedule_entries(
    day_of_week: int | None = Query(None, ge=1, le=7, description="Day (1=Mon, 7=Sun)"),
    week_type: str | None = Query(None, description="Week type: odd or even"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScheduleEntryResponse]:
    """Get all schedule entries with optional filters."""
    return await schedule_service.get_schedule_entries(db, day_of_week, week_type)


@router.post(
    "/entries",
    response_model=ScheduleEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule_entry(
    data: ScheduleEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScheduleEntryResponse:
    """Create a new schedule entry."""
    return await schedule_service.create_schedule_entry(db, data)


@router.get("/entries/{entry_id}", response_model=ScheduleEntryResponse)
async def get_schedule_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScheduleEntryResponse:
    """Get a schedule entry by ID."""
    entry = await schedule_service.get_schedule_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule entry not found",
        )
    return entry


@router.put("/entries/{entry_id}", response_model=ScheduleEntryResponse)
async def update_schedule_entry(
    entry_id: int,
    data: ScheduleEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScheduleEntryResponse:
    """Update a schedule entry."""
    entry = await schedule_service.get_schedule_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule entry not found",
        )
    return await schedule_service.update_schedule_entry(db, entry, data)


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a schedule entry."""
    entry = await schedule_service.get_schedule_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule entry not found",
        )
    await schedule_service.delete_schedule_entry(db, entry)


# Snapshot endpoints
@router.get("/snapshots", response_model=list[ScheduleSnapshotResponse])
async def get_snapshots(
    limit: int = Query(10, ge=1, le=100, description="Number of snapshots to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScheduleSnapshotResponse]:
    """Get recent schedule snapshots."""
    return await schedule_service.get_snapshots(db, limit)


@router.get("/snapshots/latest", response_model=ScheduleSnapshotResponse | None)
async def get_latest_snapshot(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScheduleSnapshotResponse | None:
    """Get the most recent schedule snapshot."""
    return await schedule_service.get_latest_snapshot(db)


# Schedule refresh endpoint
@router.post("/refresh")
async def refresh_schedule(
    force: bool = Query(False, description="Force refresh even if unchanged"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Refresh schedule from OmGU website.

    Parses the schedule, compares with the last snapshot, and updates
    the database if changes are detected.

    Args:
        force: Force update even if content hash is unchanged.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        Sync result with success status, changed flag, and entries count.
    """
    result = await schedule_service.sync_schedule(db, force=force)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Schedule refresh failed"),
        )

    return result
