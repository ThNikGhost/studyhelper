"""Work service."""

from datetime import UTC, datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import User
from src.models.work import Work, WorkStatus, WorkStatusHistory
from src.schemas.work import (
    WorkCreate,
    WorkStatusEnum,
    WorkStatusUpdate,
    WorkUpdate,
)


async def get_works(
    db: AsyncSession,
    subject_id: int | None = None,
    status: WorkStatusEnum | None = None,
    user_id: int | None = None,
    has_deadline: bool | None = None,
) -> list[Work]:
    """Get all works with optional filters."""
    query = select(Work).options(selectinload(Work.statuses))

    if subject_id is not None:
        query = query.where(Work.subject_id == subject_id)

    if has_deadline is True:
        query = query.where(Work.deadline.isnot(None))
    elif has_deadline is False:
        query = query.where(Work.deadline.is_(None))

    # Status filtering requires joining with WorkStatus
    if status is not None and user_id is not None:
        query = query.join(WorkStatus).where(
            and_(
                WorkStatus.user_id == user_id,
                WorkStatus.status == status.value,
            )
        )

    query = query.order_by(Work.deadline.asc().nullslast(), Work.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_work_by_id(
    db: AsyncSession, work_id: int, with_statuses: bool = False
) -> Work | None:
    """Get work by ID."""
    query = select(Work).where(Work.id == work_id)

    if with_statuses:
        query = query.options(selectinload(Work.statuses))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_work(
    db: AsyncSession, work_data: WorkCreate, created_by: User
) -> Work:
    """Create a new work and initialize status for all users."""
    work = Work(
        title=work_data.title,
        description=work_data.description,
        work_type=work_data.work_type.value,
        deadline=work_data.deadline,
        max_grade=work_data.max_grade,
        subject_id=work_data.subject_id,
    )
    db.add(work)
    await db.flush()

    # Get all users to create status for each (pair mode)
    users_result = await db.execute(select(User))
    users = users_result.scalars().all()

    for user in users:
        work_status = WorkStatus(
            work_id=work.id,
            user_id=user.id,
            status=WorkStatusEnum.NOT_STARTED.value,
        )
        db.add(work_status)
        await db.flush()

        # Create initial history entry
        history = WorkStatusHistory(
            work_status_id=work_status.id,
            old_status=None,
            new_status=WorkStatusEnum.NOT_STARTED.value,
            changed_at=datetime.now(UTC),
            changed_by_id=created_by.id,
        )
        db.add(history)

    await db.commit()
    await db.refresh(work)
    return work


async def update_work(
    db: AsyncSession, work: Work, work_data: WorkUpdate
) -> Work:
    """Update work."""
    update_data = work_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "work_type" and value is not None:
            value = value.value
        setattr(work, field, value)
    await db.commit()
    await db.refresh(work)
    return work


async def delete_work(db: AsyncSession, work: Work) -> None:
    """Delete work."""
    await db.delete(work)
    await db.commit()


async def get_work_status(
    db: AsyncSession, work_id: int, user_id: int
) -> WorkStatus | None:
    """Get work status for a specific user."""
    result = await db.execute(
        select(WorkStatus).where(
            and_(
                WorkStatus.work_id == work_id,
                WorkStatus.user_id == user_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def update_work_status(
    db: AsyncSession,
    work_status: WorkStatus,
    status_data: WorkStatusUpdate,
    changed_by: User,
) -> WorkStatus:
    """Update work status and create history entry."""
    old_status = work_status.status

    update_data = status_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value is not None:
            value = value.value
        setattr(work_status, field, value)

    # Create history entry if status changed
    if "status" in update_data and update_data["status"] is not None:
        history = WorkStatusHistory(
            work_status_id=work_status.id,
            old_status=old_status,
            new_status=work_status.status,
            changed_at=datetime.now(UTC),
            changed_by_id=changed_by.id,
        )
        db.add(history)

    await db.commit()
    await db.refresh(work_status)
    return work_status


async def get_work_status_history(
    db: AsyncSession, work_status_id: int
) -> list[WorkStatusHistory]:
    """Get status change history."""
    result = await db.execute(
        select(WorkStatusHistory)
        .where(WorkStatusHistory.work_status_id == work_status_id)
        .order_by(WorkStatusHistory.changed_at.desc())
    )
    return list(result.scalars().all())


async def get_upcoming_works(
    db: AsyncSession, user_id: int, limit: int = 10
) -> list[Work]:
    """Get works with upcoming deadlines."""
    now = datetime.now(UTC)

    query = (
        select(Work)
        .options(selectinload(Work.statuses), selectinload(Work.subject))
        .where(
            and_(
                Work.deadline.isnot(None),
                Work.deadline > now,
            )
        )
        .order_by(Work.deadline.asc())
        .limit(limit)
    )

    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def ensure_work_status_exists(
    db: AsyncSession, work: Work, user: User
) -> WorkStatus:
    """Ensure work status exists for user (create if missing)."""
    status = await get_work_status(db, work.id, user.id)
    if status is None:
        status = WorkStatus(
            work_id=work.id,
            user_id=user.id,
            status=WorkStatusEnum.NOT_STARTED.value,
        )
        db.add(status)
        await db.flush()

        history = WorkStatusHistory(
            work_status_id=status.id,
            old_status=None,
            new_status=WorkStatusEnum.NOT_STARTED.value,
            changed_at=datetime.now(UTC),
            changed_by_id=user.id,
        )
        db.add(history)
        await db.commit()
        await db.refresh(status)

    return status
