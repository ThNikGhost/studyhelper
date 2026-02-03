"""Subjects router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from src.schemas.work import WorkStatusResponse, WorkWithStatusResponse
from src.services import semester as semester_service
from src.services import subject as subject_service
from src.services import work as work_service

router = APIRouter()


@router.get("", response_model=list[SubjectResponse])
async def get_subjects(
    semester_id: int | None = Query(None, description="Filter by semester ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SubjectResponse]:
    """Get all subjects, optionally filtered by semester."""
    return await subject_service.get_subjects(db, semester_id=semester_id)


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectResponse:
    """Create a new subject."""
    # Verify semester exists
    semester = await semester_service.get_semester_by_id(db, subject_data.semester_id)
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found",
        )
    return await subject_service.create_subject(db, subject_data)


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectResponse:
    """Get a subject by ID."""
    subject = await subject_service.get_subject_by_id(db, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectResponse:
    """Update a subject."""
    subject = await subject_service.get_subject_by_id(db, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )

    # If changing semester, verify new semester exists
    if subject_data.semester_id is not None:
        semester = await semester_service.get_semester_by_id(
            db, subject_data.semester_id
        )
        if not semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Semester not found",
            )

    return await subject_service.update_subject(db, subject, subject_data)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a subject."""
    subject = await subject_service.get_subject_by_id(db, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )
    await subject_service.delete_subject(db, subject)


@router.get("/{subject_id}/works", response_model=list[WorkWithStatusResponse])
async def get_subject_works(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkWithStatusResponse]:
    """Get all works for a subject."""
    subject = await subject_service.get_subject_by_id(db, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )

    works = await work_service.get_works(db, subject_id=subject_id)

    result = []
    for work in works:
        work_dict = WorkWithStatusResponse.model_validate(work)
        for ws in work.statuses:
            if ws.user_id == current_user.id:
                work_dict.my_status = WorkStatusResponse.model_validate(ws)
                break
        result.append(work_dict)

    return result
