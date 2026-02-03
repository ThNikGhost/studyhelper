"""Semesters router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.semester import SemesterCreate, SemesterResponse, SemesterUpdate
from src.services import semester as semester_service

router = APIRouter()


@router.get("", response_model=list[SemesterResponse])
async def get_semesters(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SemesterResponse]:
    """Get all semesters."""
    return await semester_service.get_semesters(db)


@router.post("", response_model=SemesterResponse, status_code=status.HTTP_201_CREATED)
async def create_semester(
    semester_data: SemesterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SemesterResponse:
    """Create a new semester."""
    return await semester_service.create_semester(db, semester_data)


@router.get("/current", response_model=SemesterResponse | None)
async def get_current_semester(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SemesterResponse | None:
    """Get the current semester."""
    return await semester_service.get_current_semester(db)


@router.get("/{semester_id}", response_model=SemesterResponse)
async def get_semester(
    semester_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SemesterResponse:
    """Get a semester by ID."""
    semester = await semester_service.get_semester_by_id(db, semester_id)
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found",
        )
    return semester


@router.put("/{semester_id}", response_model=SemesterResponse)
async def update_semester(
    semester_id: int,
    semester_data: SemesterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SemesterResponse:
    """Update a semester."""
    semester = await semester_service.get_semester_by_id(db, semester_id)
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found",
        )
    return await semester_service.update_semester(db, semester, semester_data)


@router.delete("/{semester_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_semester(
    semester_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a semester."""
    semester = await semester_service.get_semester_by_id(db, semester_id)
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found",
        )
    await semester_service.delete_semester(db, semester)


@router.put("/{semester_id}/set-current", response_model=SemesterResponse)
async def set_current_semester(
    semester_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SemesterResponse:
    """Set a semester as the current one."""
    semester = await semester_service.get_semester_by_id(db, semester_id)
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found",
        )
    return await semester_service.set_current_semester(db, semester)
