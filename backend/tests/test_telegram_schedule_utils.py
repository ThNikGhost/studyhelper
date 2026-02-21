"""Unit tests for telegram/schedule_utils.py."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule import ScheduleEntry
from src.models.semester import Semester
from src.models.subject import Subject
from src.models.user import User
from src.models.work import Work
from src.telegram.schedule_utils import (
    filter_works_by_hidden_subjects,
    get_filtered_current_lesson,
    get_filtered_day_schedule,
)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with no preferences."""
    user = User(
        email="test@example.com",
        password_hash="hashed",
        name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_semester(db_session: AsyncSession) -> Semester:
    """Create a test semester."""
    semester = Semester(
        number=1,
        year_start=2024,
        year_end=2025,
        name="1 семестр 2024-2025",
        start_date=date(2024, 9, 1),
        end_date=date(2025, 1, 31),
    )
    db_session.add(semester)
    await db_session.commit()
    await db_session.refresh(semester)
    return semester


@pytest.fixture
async def math_subject(db_session: AsyncSession, test_semester: Semester) -> Subject:
    """Create a math subject."""
    subject = Subject(
        name="Математический анализ",
        short_name="Матан",
        semester_id=test_semester.id,
    )
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    return subject


@pytest.fixture
async def physics_subject(db_session: AsyncSession, test_semester: Semester) -> Subject:
    """Create a physics subject."""
    subject = Subject(
        name="Физика",
        short_name="Физ",
        semester_id=test_semester.id,
    )
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    return subject


@pytest.fixture
async def schedule_today(
    db_session: AsyncSession, math_subject: Subject, physics_subject: Subject
) -> list[ScheduleEntry]:
    """Create schedule entries for today."""
    from src.services.schedule import OMSK_TZ

    today = datetime.now(OMSK_TZ).date()
    day_of_week = today.isoweekday()

    entries = [
        ScheduleEntry(
            lesson_date=today,
            day_of_week=day_of_week,
            start_time=time(9, 0),
            end_time=time(10, 30),
            subject_name=math_subject.name,
            subject_id=math_subject.id,
            lesson_type="lecture",
            teacher_name="Иванов И.И.",
            room="301",
        ),
        ScheduleEntry(
            lesson_date=today,
            day_of_week=day_of_week,
            start_time=time(10, 45),
            end_time=time(12, 15),
            subject_name=physics_subject.name,
            subject_id=physics_subject.id,
            lesson_type="lab",
            teacher_name="Петров П.П.",
            room="205",
        ),
    ]
    for entry in entries:
        db_session.add(entry)
    await db_session.commit()
    return entries


@pytest.mark.asyncio
class TestGetFilteredDaySchedule:
    """Tests for get_filtered_day_schedule()."""

    async def test_no_hidden_subjects(
        self,
        db_session: AsyncSession,
        test_user: User,
        schedule_today: list[ScheduleEntry],
    ):
        """Test schedule returns all entries when no subjects are hidden."""
        result = await get_filtered_day_schedule(db_session, test_user)

        assert len(result.entries) == 2
        assert result.entries[0].subject_name == "Математический анализ"
        assert result.entries[1].subject_name == "Физика"

    async def test_fully_hidden_subject(
        self,
        db_session: AsyncSession,
        test_user: User,
        math_subject: Subject,
        schedule_today: list[ScheduleEntry],
    ):
        """Test fully hidden subject (hidden_subjects[id] = null) is filtered out."""
        # Hide math subject completely
        test_user.hidden_subjects = {str(math_subject.id): None}
        await db_session.commit()

        result = await get_filtered_day_schedule(db_session, test_user)

        assert len(result.entries) == 1
        assert result.entries[0].subject_name == "Физика"

    async def test_per_type_hidden(
        self,
        db_session: AsyncSession,
        test_user: User,
        physics_subject: Subject,
        schedule_today: list[ScheduleEntry],
    ):
        """Test per-type hiding (hidden_subjects[id] = ["lab"]) filters only lab lessons."""
        # Hide only physics lab lessons
        test_user.hidden_subjects = {str(physics_subject.id): ["lab"]}
        await db_session.commit()

        result = await get_filtered_day_schedule(db_session, test_user)

        assert len(result.entries) == 1
        assert result.entries[0].subject_name == "Математический анализ"


@pytest.mark.asyncio
class TestGetFilteredCurrentLesson:
    """Tests for get_filtered_current_lesson()."""

    async def test_next_is_hidden(
        self,
        db_session: AsyncSession,
        test_user: User,
        physics_subject: Subject,
    ):
        """Test next lesson is filtered if hidden."""
        today = date.today()
        day_of_week = today.isoweekday()

        # Create future lesson (math at 9:00, physics at 10:45)
        math_entry = ScheduleEntry(
            lesson_date=today,
            day_of_week=day_of_week,
            start_time=time(9, 0),
            end_time=time(10, 30),
            subject_name="Математический анализ",
            lesson_type="lecture",
        )
        physics_entry = ScheduleEntry(
            lesson_date=today,
            day_of_week=day_of_week,
            start_time=time(10, 45),
            end_time=time(12, 15),
            subject_name=physics_subject.name,
            subject_id=physics_subject.id,
            lesson_type="lab",
        )
        db_session.add_all([math_entry, physics_entry])
        await db_session.commit()

        # Hide physics completely
        test_user.hidden_subjects = {str(physics_subject.id): None}
        await db_session.commit()

        result = await get_filtered_current_lesson(db_session, test_user)

        # Current lesson should be None (not happening now)
        # Next lesson should be math (physics is hidden)
        # Note: This test depends on current time - math should be in future
        assert (
            result.next is None or result.next.subject_name == "Математический анализ"
        )


@pytest.mark.asyncio
class TestFilterWorksByHiddenSubjects:
    """Tests for filter_works_by_hidden_subjects()."""

    async def test_fully_hidden(self, db_session: AsyncSession, math_subject: Subject):
        """Test work for fully hidden subject is filtered out."""
        work = Work(
            title="Lab 1",
            work_type="lab",
            subject_id=math_subject.id,
            deadline=datetime.now(UTC) + timedelta(days=7),
        )
        db_session.add(work)
        await db_session.commit()
        await db_session.refresh(work)

        # Hide math completely
        hidden_config = {math_subject.name: None}

        result = filter_works_by_hidden_subjects([work], hidden_config)

        assert len(result) == 0

    async def test_per_type_not_filtered(
        self, db_session: AsyncSession, math_subject: Subject
    ):
        """Test per-type hiding does NOT filter works (works are not lesson-type specific)."""
        work = Work(
            title="Lab 1",
            work_type="lab",
            subject_id=math_subject.id,
            deadline=datetime.now(UTC) + timedelta(days=7),
        )
        db_session.add(work)
        await db_session.commit()
        await db_session.refresh(work)

        # Hide only math lab lessons (per-type)
        hidden_config = {math_subject.name: {"lab"}}

        result = filter_works_by_hidden_subjects([work], hidden_config)

        # Work should NOT be filtered (per-type hiding doesn't apply to works)
        assert len(result) == 1
        assert result[0].title == "Lab 1"

    async def test_subject_not_hidden(
        self, db_session: AsyncSession, math_subject: Subject
    ):
        """Test work whose subject is not in hidden_config is not filtered."""
        work = Work(
            title="General Assignment",
            work_type="homework",
            subject_id=math_subject.id,
            deadline=datetime.now(UTC) + timedelta(days=7),
        )
        db_session.add(work)
        await db_session.commit()
        await db_session.refresh(work)

        # Hidden config does not include math_subject
        hidden_config = {"Some Other Subject": None}

        result = filter_works_by_hidden_subjects([work], hidden_config)

        # Work should NOT be filtered (its subject is not hidden)
        assert len(result) == 1
        assert result[0].title == "General Assignment"
