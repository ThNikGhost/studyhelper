"""LK (личный кабинет) service.

Business logic for LK credential management and data synchronization.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.lk import LkCredentials, SemesterDiscipline, SessionGrade
from src.parser.lk_exceptions import LkAuthError
from src.parser.lk_parser import LkParser, LkStudentData
from src.schemas.lk import LkCredentialsCreate
from src.utils.crypto import decrypt_credential, encrypt_credential
from src.utils.exceptions import LkCredentialsNotFound, LkSyncError

logger = logging.getLogger(__name__)


async def get_credentials(db: AsyncSession, user_id: int) -> LkCredentials | None:
    """Get LK credentials for user.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        LkCredentials if exists, None otherwise.
    """
    result = await db.execute(
        select(LkCredentials).where(LkCredentials.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def save_credentials(
    db: AsyncSession, user_id: int, data: LkCredentialsCreate
) -> LkCredentials:
    """Encrypt and save LK credentials (upsert).

    Args:
        db: Database session.
        user_id: User ID.
        data: Credentials to save.

    Returns:
        Saved or updated LkCredentials.
    """
    creds = await get_credentials(db, user_id)

    encrypted_email = encrypt_credential(data.email)
    encrypted_password = encrypt_credential(data.password)

    if creds:
        creds.encrypted_email = encrypted_email
        creds.encrypted_password = encrypted_password
        logger.info("Updated LK credentials for user %d", user_id)
    else:
        creds = LkCredentials(
            user_id=user_id,
            encrypted_email=encrypted_email,
            encrypted_password=encrypted_password,
        )
        db.add(creds)
        logger.info("Created LK credentials for user %d", user_id)

    await db.commit()
    await db.refresh(creds)
    return creds


async def delete_credentials(db: AsyncSession, user_id: int) -> bool:
    """Delete LK credentials for user.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        True if credentials were deleted, False if not found.
    """
    result = await db.execute(
        delete(LkCredentials).where(LkCredentials.user_id == user_id)
    )
    await db.commit()
    deleted = result.rowcount > 0
    if deleted:
        logger.info("Deleted LK credentials for user %d", user_id)
    return deleted


async def verify_credentials(email: str, password: str) -> bool:
    """Verify LK credentials by attempting login.

    Args:
        email: LK email.
        password: LK password.

    Returns:
        True if credentials are valid, False otherwise.
    """
    try:
        async with LkParser() as parser:
            return await parser.login(email, password)
    except LkAuthError:
        return False


async def sync_from_lk(db: AsyncSession, user_id: int) -> tuple[int, int]:
    """Sync grades and disciplines from LK.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        Tuple of (grades_count, disciplines_count).

    Raises:
        LkCredentialsNotFound: If no credentials saved.
        LkSyncError: If sync fails.
    """
    creds = await get_credentials(db, user_id)
    if not creds:
        raise LkCredentialsNotFound()

    email = decrypt_credential(creds.encrypted_email)
    password = decrypt_credential(creds.encrypted_password)

    try:
        async with LkParser() as parser:
            if not await parser.login(email, password):
                raise LkSyncError("Authentication failed - check credentials")

            data = await parser.fetch_student_data()
    except LkAuthError as e:
        raise LkSyncError(f"Authentication error: {e}") from e
    except Exception as e:
        raise LkSyncError(f"Failed to fetch data: {e}") from e

    # Sync grades
    grades_count = await _sync_grades(db, user_id, data)

    # Sync disciplines
    disciplines_count = await _sync_disciplines(db, user_id, data)

    # Update last_sync_at
    creds.last_sync_at = datetime.now(UTC)
    await db.commit()

    logger.info(
        "Synced LK data for user %d: %d grades, %d disciplines",
        user_id,
        grades_count,
        disciplines_count,
    )

    return grades_count, disciplines_count


async def _sync_grades(db: AsyncSession, user_id: int, data: LkStudentData) -> int:
    """Sync session grades (upsert).

    Args:
        db: Database session.
        user_id: User ID.
        data: Student data from LK.

    Returns:
        Number of grades synced.
    """
    count = 0
    now = datetime.now(UTC)

    for session in data.sessions:
        session_number = session.get("number", "")
        entries = session.get("entries", [])

        for entry in entries:
            subject_name = entry.get("subject", "")
            result = entry.get("result", "")

            if not subject_name:
                continue

            # Use PostgreSQL upsert (INSERT ... ON CONFLICT UPDATE)
            stmt = pg_insert(SessionGrade).values(
                user_id=user_id,
                session_number=session_number,
                subject_name=subject_name,
                result=result,
                synced_at=now,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["user_id", "session_number", "subject_name"],
                set_={"result": result, "synced_at": now},
            )
            await db.execute(stmt)
            count += 1

    await db.commit()
    return count


async def _sync_disciplines(db: AsyncSession, user_id: int, data: LkStudentData) -> int:
    """Sync semester disciplines (upsert).

    Args:
        db: Database session.
        user_id: User ID.
        data: Student data from LK.

    Returns:
        Number of disciplines synced.
    """
    count = 0
    now = datetime.now(UTC)

    for item in data.sem_info:
        semester_number = item.get("semester", 0)
        discipline_name = item.get("discipline", "")
        control_form = item.get("controlForm", "")
        hours = item.get("length", 0)

        if not discipline_name:
            continue

        # Ensure semester_number is int
        try:
            semester_number = int(semester_number)
        except (ValueError, TypeError):
            continue

        # Ensure hours is int
        try:
            hours = int(hours)
        except (ValueError, TypeError):
            hours = 0

        # Use PostgreSQL upsert
        stmt = pg_insert(SemesterDiscipline).values(
            user_id=user_id,
            semester_number=semester_number,
            discipline_name=discipline_name,
            control_form=control_form,
            hours=hours,
            synced_at=now,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_id", "semester_number", "discipline_name"],
            set_={
                "control_form": control_form,
                "hours": hours,
                "synced_at": now,
            },
        )
        await db.execute(stmt)
        count += 1

    await db.commit()
    return count


async def get_grades(
    db: AsyncSession,
    user_id: int,
    session_number: str | None = None,
) -> list[SessionGrade]:
    """Get synced grades for user.

    Args:
        db: Database session.
        user_id: User ID.
        session_number: Optional filter by session.

    Returns:
        List of SessionGrade objects.
    """
    query = select(SessionGrade).where(SessionGrade.user_id == user_id)

    if session_number:
        query = query.where(SessionGrade.session_number == session_number)

    query = query.order_by(
        SessionGrade.session_number.desc(),
        SessionGrade.subject_name,
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_disciplines(
    db: AsyncSession,
    user_id: int,
    semester_number: int | None = None,
) -> list[SemesterDiscipline]:
    """Get synced disciplines for user.

    Args:
        db: Database session.
        user_id: User ID.
        semester_number: Optional filter by semester.

    Returns:
        List of SemesterDiscipline objects.
    """
    query = select(SemesterDiscipline).where(SemesterDiscipline.user_id == user_id)

    if semester_number is not None:
        query = query.where(SemesterDiscipline.semester_number == semester_number)

    query = query.order_by(
        SemesterDiscipline.semester_number,
        SemesterDiscipline.discipline_name,
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_unique_sessions(db: AsyncSession, user_id: int) -> list[str]:
    """Get list of unique session numbers for user.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        List of unique session numbers sorted descending.
    """
    result = await db.execute(
        select(SessionGrade.session_number)
        .where(SessionGrade.user_id == user_id)
        .distinct()
        .order_by(SessionGrade.session_number.desc())
    )
    return [row[0] for row in result.all()]


async def get_unique_semesters(db: AsyncSession, user_id: int) -> list[int]:
    """Get list of unique semester numbers for user.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        List of unique semester numbers sorted ascending.
    """
    result = await db.execute(
        select(SemesterDiscipline.semester_number)
        .where(SemesterDiscipline.user_id == user_id)
        .distinct()
        .order_by(SemesterDiscipline.semester_number)
    )
    return [row[0] for row in result.all()]
