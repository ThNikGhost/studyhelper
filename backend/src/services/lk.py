"""LK (личный кабинет) service.

Business logic for LK credential management and data synchronization.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.lk import LkCredentials, SemesterDiscipline, SessionGrade
from src.models.semester import Semester
from src.models.subject import Subject
from src.parser.lk_exceptions import LkAuthError
from src.parser.lk_parser import LkParser, LkStudentData
from src.schemas.lk import LkCredentialsCreate, LkImportResult
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

    # Log raw data for debugging
    logger.debug(
        "Raw LK data: sessions=%d, sem_info=%d", len(data.sessions), len(data.sem_info)
    )
    logger.debug("Sessions: %s", data.sessions[:2] if data.sessions else "empty")
    logger.debug("SemInfo: %s", data.sem_info[:2] if data.sem_info else "empty")

    # Sync grades
    try:
        grades_count = await _sync_grades(db, user_id, data)
    except Exception as e:
        logger.exception("Failed to sync grades: %s", e)
        raise LkSyncError(f"Failed to sync grades: {e}") from e

    # Sync disciplines
    try:
        disciplines_count = await _sync_disciplines(db, user_id, data)
    except Exception as e:
        logger.exception("Failed to sync disciplines: %s", e)
        raise LkSyncError(f"Failed to sync disciplines: {e}") from e

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

    # semInfo structure: [{number: 1, entries: [{discipline, controlForm, length}, ...]}, ...]
    for semester in data.sem_info:
        semester_number = semester.get("number", 0)

        # Ensure semester_number is int
        try:
            semester_number = int(semester_number)
        except (ValueError, TypeError):
            continue

        entries = semester.get("entries", [])
        for item in entries:
            discipline_name = item.get("discipline", "")
            control_form = item.get("controlForm", "")
            hours = item.get("length", 0)

            if not discipline_name:
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


async def _determine_current_semester(
    db: AsyncSession,
    user_id: int,
    max_discipline_semester: int,
) -> int:
    """Determine current semester from session grades.

    Parses session_number (format "5 2025/2026") to extract the semester
    number. Current semester = max(session_numbers) + 1, capped by
    max_discipline_semester.

    Args:
        db: Database session.
        user_id: User ID.
        max_discipline_semester: Highest semester in the study plan.

    Returns:
        Current semester number (1-based).
    """
    grades = await get_grades(db, user_id)
    if not grades:
        return 1

    session_numbers: list[int] = []
    for grade in grades:
        # session_number format: "5 2025/2026" → extract first part
        parts = grade.session_number.strip().split()
        if not parts:
            logger.warning("Empty session_number for user %d", user_id)
            continue
        try:
            session_numbers.append(int(parts[0]))
        except (ValueError, TypeError):
            logger.warning(
                "Invalid session_number format: %s",
                grade.session_number,
            )
            continue

    if not session_numbers:
        return 1

    current = max(session_numbers) + 1
    return min(current, max_discipline_semester)


async def import_to_app(db: AsyncSession, user_id: int) -> LkImportResult:
    """Import semesters and subjects from LK data to app.

    Creates or updates semesters and subjects based on previously
    synced SemesterDiscipline records.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        LkImportResult with counts of created/updated records.

    Raises:
        LkCredentialsNotFound: If no credentials saved.
        LkSyncError: If no disciplines to import.
    """
    # Check if user has synced disciplines
    disciplines = await get_disciplines(db, user_id)
    if not disciplines:
        raise LkSyncError("No disciplines to import. Sync from LK first.")

    # Get current academic year based on date
    now = datetime.now(UTC)
    # Academic year starts in September
    if now.month >= 9:
        current_year_start = now.year
        current_year_end = now.year + 1
    else:
        current_year_start = now.year - 1
        current_year_end = now.year

    # Group disciplines by semester number
    disciplines_by_semester: dict[int, list[SemesterDiscipline]] = {}
    for disc in disciplines:
        if disc.semester_number not in disciplines_by_semester:
            disciplines_by_semester[disc.semester_number] = []
        disciplines_by_semester[disc.semester_number].append(disc)

    semesters_created = 0
    semesters_updated = 0
    subjects_created = 0
    subjects_updated = 0

    # Determine current semester from session grades
    max_discipline_semester = max(disciplines_by_semester.keys())
    current_semester = await _determine_current_semester(
        db,
        user_id,
        max_discipline_semester,
    )

    # Process each semester
    for semester_number, sem_disciplines in disciplines_by_semester.items():
        # Calculate how many years back this semester is
        years_back = (current_semester - semester_number) // 2
        year_start = current_year_start - years_back
        year_end = current_year_end - years_back

        # Adjust for even/odd semester within academic year
        # Odd = fall (first half), Even = spring (second half)
        # Example: current=6 (spring 2026), sem=5 (fall 2025)
        # years_back = (6-5)//2 = 0, but sem 5 is in prev academic year → -1
        if current_semester % 2 == 0 and semester_number % 2 == 1:
            year_start -= 1
            year_end -= 1

        # Default semester dates
        if semester_number % 2 == 1:  # Fall
            default_start = date(year_start, 9, 1)
            default_end = date(year_start, 12, 30)
        else:  # Spring
            default_start = date(year_end, 2, 9)
            default_end = date(year_end, 7, 7)

        # Generate semester name
        season = "Осенний" if semester_number % 2 == 1 else "Весенний"
        name = f"{season} семестр {year_start}/{year_end}"

        # Find or create semester
        result = await db.execute(
            select(Semester).where(Semester.number == semester_number)
        )
        semester = result.scalar_one_or_none()

        if semester:
            # Update existing semester
            semester.year_start = year_start
            semester.year_end = year_end
            semester.name = name
            semester.is_current = semester_number == current_semester
            # Fill dates only if not manually set
            if semester.start_date is None:
                semester.start_date = default_start
            if semester.end_date is None:
                semester.end_date = default_end
            semesters_updated += 1
        else:
            # Create new semester
            semester = Semester(
                number=semester_number,
                year_start=year_start,
                year_end=year_end,
                name=name,
                is_current=semester_number == current_semester,
                start_date=default_start,
                end_date=default_end,
            )
            db.add(semester)
            await db.flush()
            semesters_created += 1

        # Create/update subjects for this semester
        for disc in sem_disciplines:
            # Find existing subject by name and semester
            result = await db.execute(
                select(Subject).where(
                    Subject.name == disc.discipline_name,
                    Subject.semester_id == semester.id,
                )
            )
            subject = result.scalar_one_or_none()

            if subject:
                # Update total_hours if changed
                if subject.total_hours != disc.hours:
                    subject.total_hours = disc.hours
                    subjects_updated += 1
            else:
                # Create new subject
                subject = Subject(
                    name=disc.discipline_name,
                    semester_id=semester.id,
                    total_hours=disc.hours,
                )
                db.add(subject)
                subjects_created += 1

    await db.commit()

    logger.info(
        "Imported from LK for user %d: %d/%d semesters, %d/%d subjects",
        user_id,
        semesters_created,
        semesters_updated,
        subjects_created,
        subjects_updated,
    )

    return LkImportResult(
        semesters_created=semesters_created,
        semesters_updated=semesters_updated,
        subjects_created=subjects_created,
        subjects_updated=subjects_updated,
    )
