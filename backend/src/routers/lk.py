"""LK (личный кабинет) router.

API endpoints for LK credential management and data synchronization.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.lk import (
    LkCredentialsCreate,
    LkStatusResponse,
    LkSyncResponse,
    SemesterDisciplineResponse,
    SessionGradeResponse,
)
from src.services import lk as lk_service

router = APIRouter()


@router.get("/status", response_model=LkStatusResponse)
async def get_lk_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LkStatusResponse:
    """Get LK connection status for current user.

    Returns whether credentials are saved and last sync timestamp.
    """
    creds = await lk_service.get_credentials(db, current_user.id)
    return LkStatusResponse(
        has_credentials=creds is not None,
        last_sync_at=creds.last_sync_at if creds else None,
    )


@router.post("/credentials", status_code=status.HTTP_201_CREATED)
async def save_credentials(
    data: LkCredentialsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Save LK credentials (encrypted).

    Credentials are encrypted before storage using Fernet.
    If credentials already exist, they are updated.
    """
    await lk_service.save_credentials(db, current_user.id, data)
    return {"message": "Credentials saved successfully"}


@router.delete("/credentials", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credentials(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete LK credentials.

    Also clears last_sync_at timestamp.
    """
    await lk_service.delete_credentials(db, current_user.id)


@router.post("/verify")
async def verify_credentials(
    data: LkCredentialsCreate,
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    """Verify LK credentials without saving.

    Attempts to authenticate with provided credentials.
    Does NOT save credentials if successful.
    """
    is_valid = await lk_service.verify_credentials(data.email, data.password)
    return {"valid": is_valid}


@router.post("/sync", response_model=LkSyncResponse)
async def sync_from_lk(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LkSyncResponse:
    """Sync data from LK.

    Requires saved credentials. Fetches grades and disciplines
    from LK and stores them in the database.

    Raises:
        400: If credentials not saved.
        502: If LK sync fails.
    """
    grades_count, disciplines_count = await lk_service.sync_from_lk(db, current_user.id)
    creds = await lk_service.get_credentials(db, current_user.id)
    return LkSyncResponse(
        grades_synced=grades_count,
        disciplines_synced=disciplines_count,
        last_sync_at=creds.last_sync_at,  # type: ignore
    )


@router.get("/grades", response_model=list[SessionGradeResponse])
async def get_grades(
    session: str | None = Query(None, description="Filter by session number"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SessionGradeResponse]:
    """Get synced session grades.

    Returns grades from previous sessions (exams, zachets).
    Optionally filter by session number.
    """
    grades = await lk_service.get_grades(db, current_user.id, session)
    return [SessionGradeResponse.model_validate(g) for g in grades]


@router.get("/grades/sessions", response_model=list[str])
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """Get list of unique session numbers.

    Useful for populating session filter dropdown.
    """
    return await lk_service.get_unique_sessions(db, current_user.id)


@router.get("/disciplines", response_model=list[SemesterDisciplineResponse])
async def get_disciplines(
    semester: int | None = Query(None, ge=1, le=12, description="Filter by semester"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SemesterDisciplineResponse]:
    """Get synced study plan disciplines.

    Returns curriculum from study plan.
    Optionally filter by semester number.
    """
    disciplines = await lk_service.get_disciplines(db, current_user.id, semester)
    return [SemesterDisciplineResponse.model_validate(d) for d in disciplines]


@router.get("/disciplines/semesters", response_model=list[int])
async def get_semesters(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[int]:
    """Get list of unique semester numbers.

    Useful for populating semester filter dropdown.
    """
    return await lk_service.get_unique_semesters(db, current_user.id)
