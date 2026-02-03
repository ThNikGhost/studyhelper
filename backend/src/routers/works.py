"""Works router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.work import (
    UpcomingWorkResponse,
    WorkCreate,
    WorkResponse,
    WorkStatusEnum,
    WorkStatusHistoryResponse,
    WorkStatusResponse,
    WorkStatusUpdate,
    WorkUpdate,
    WorkWithStatusResponse,
)
from src.services import subject as subject_service
from src.services import work as work_service

router = APIRouter()


@router.get("", response_model=list[WorkWithStatusResponse])
async def get_works(
    subject_id: int | None = Query(None, description="Filter by subject ID"),
    work_status: WorkStatusEnum | None = Query(
        None, alias="status", description="Filter by status"
    ),
    has_deadline: bool | None = Query(None, description="Filter by deadline presence"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkWithStatusResponse]:
    """Get all works with optional filters."""
    works = await work_service.get_works(
        db,
        subject_id=subject_id,
        status=work_status,
        user_id=current_user.id,
        has_deadline=has_deadline,
    )

    result = []
    for work in works:
        work_dict = WorkWithStatusResponse.model_validate(work)
        # Find current user's status
        for ws in work.statuses:
            if ws.user_id == current_user.id:
                work_dict.my_status = WorkStatusResponse.model_validate(ws)
                break
        result.append(work_dict)

    return result


@router.post(
    "", response_model=WorkWithStatusResponse, status_code=status.HTTP_201_CREATED
)
async def create_work(
    work_data: WorkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkWithStatusResponse:
    """Create a new work."""
    # Verify subject exists
    subject = await subject_service.get_subject_by_id(db, work_data.subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )

    work = await work_service.create_work(db, work_data, current_user)
    work = await work_service.get_work_by_id(db, work.id, with_statuses=True)

    result = WorkWithStatusResponse.model_validate(work)
    for ws in work.statuses:
        if ws.user_id == current_user.id:
            result.my_status = WorkStatusResponse.model_validate(ws)
            break

    return result


@router.get("/upcoming", response_model=list[UpcomingWorkResponse])
async def get_upcoming_works(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of works"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UpcomingWorkResponse]:
    """Get works with upcoming deadlines."""
    works = await work_service.get_upcoming_works(db, current_user.id, limit=limit)

    result = []
    for work in works:
        my_status = None
        for ws in work.statuses:
            if ws.user_id == current_user.id:
                my_status = WorkStatusEnum(ws.status)
                break

        result.append(
            UpcomingWorkResponse(
                id=work.id,
                title=work.title,
                work_type=work.work_type,
                deadline=work.deadline,
                subject_id=work.subject_id,
                subject_name=work.subject.name,
                my_status=my_status,
            )
        )

    return result


@router.get("/{work_id}", response_model=WorkWithStatusResponse)
async def get_work(
    work_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkWithStatusResponse:
    """Get a work by ID."""
    work = await work_service.get_work_by_id(db, work_id, with_statuses=True)
    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    result = WorkWithStatusResponse.model_validate(work)
    for ws in work.statuses:
        if ws.user_id == current_user.id:
            result.my_status = WorkStatusResponse.model_validate(ws)
            break

    return result


@router.put("/{work_id}", response_model=WorkResponse)
async def update_work(
    work_id: int,
    work_data: WorkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkResponse:
    """Update a work."""
    work = await work_service.get_work_by_id(db, work_id)
    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    # If changing subject, verify new subject exists
    if work_data.subject_id is not None:
        subject = await subject_service.get_subject_by_id(db, work_data.subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found",
            )

    return await work_service.update_work(db, work, work_data)


@router.delete("/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work(
    work_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a work."""
    work = await work_service.get_work_by_id(db, work_id)
    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )
    await work_service.delete_work(db, work)


@router.put("/{work_id}/status", response_model=WorkStatusResponse)
async def update_work_status(
    work_id: int,
    status_data: WorkStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkStatusResponse:
    """Update work status for current user."""
    work = await work_service.get_work_by_id(db, work_id)
    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    work_status = await work_service.ensure_work_status_exists(db, work, current_user)
    return await work_service.update_work_status(
        db, work_status, status_data, current_user
    )


@router.get("/{work_id}/history", response_model=list[WorkStatusHistoryResponse])
async def get_work_status_history(
    work_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkStatusHistoryResponse]:
    """Get status change history for current user's work status."""
    work = await work_service.get_work_by_id(db, work_id)
    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    work_status = await work_service.get_work_status(db, work_id, current_user.id)
    if not work_status:
        return []

    return await work_service.get_work_status_history(db, work_status.id)
