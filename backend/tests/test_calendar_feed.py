"""Tests for calendar feed service and API."""

from datetime import UTC, date, datetime, time

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule import ScheduleEntry
from src.models.semester import Semester
from src.models.subject import Subject
from src.models.user import User
from src.models.work import Work
from src.services import calendar_feed as cal_service


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="cal_test@example.com",
        password_hash="fakehash",
        name="Cal Test User",
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def user_with_prefs(db_session: AsyncSession) -> User:
    """Create a user with subgroup and PE teacher preferences."""
    user = User(
        email="cal_prefs@example.com",
        password_hash="fakehash",
        name="Cal Prefs User",
        preferred_subgroup=1,
        preferred_pe_teacher="Иванов И.И.",
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def semester(db_session: AsyncSession) -> Semester:
    """Create a current semester."""
    sem = Semester(
        number=1,
        year_start=2025,
        year_end=2026,
        name="1 семестр 2025/2026",
        is_current=True,
        start_date=date(2025, 9, 1),
        end_date=date(2026, 6, 30),
    )
    db_session.add(sem)
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(sem)
    return sem


@pytest.fixture
async def schedule_entries(
    db_session: AsyncSession, semester: Semester
) -> list[ScheduleEntry]:
    """Create sample schedule entries."""
    entries = [
        ScheduleEntry(
            lesson_date=date(2026, 2, 16),
            day_of_week=1,
            start_time=time(8, 0),
            end_time=time(9, 30),
            subject_name="Математика",
            lesson_type="lecture",
            teacher_name="Петров П.П.",
            room="101",
            building="Корпус 1",
        ),
        ScheduleEntry(
            lesson_date=date(2026, 2, 16),
            day_of_week=1,
            start_time=time(9, 45),
            end_time=time(11, 15),
            subject_name="Физика",
            lesson_type="practice",
            teacher_name="Сидоров С.С.",
            room="202",
            building="Корпус 2",
            subgroup=1,
        ),
        ScheduleEntry(
            lesson_date=date(2026, 2, 16),
            day_of_week=1,
            start_time=time(9, 45),
            end_time=time(11, 15),
            subject_name="Физика",
            lesson_type="practice",
            teacher_name="Козлов К.К.",
            room="203",
            building="Корпус 2",
            subgroup=2,
        ),
        ScheduleEntry(
            lesson_date=date(2026, 2, 17),
            day_of_week=2,
            start_time=time(8, 0),
            end_time=time(9, 30),
            subject_name="Физическая культура",
            lesson_type="practice",
            teacher_name="Иванов И.И.",
            room="Зал 1",
            building="Спортзал",
        ),
        ScheduleEntry(
            lesson_date=date(2026, 2, 17),
            day_of_week=2,
            start_time=time(8, 0),
            end_time=time(9, 30),
            subject_name="Физическая культура",
            lesson_type="practice",
            teacher_name="Смирнов С.С.",
            room="Зал 2",
            building="Спортзал",
        ),
    ]
    for e in entries:
        db_session.add(e)
    await db_session.flush()
    await db_session.commit()
    for e in entries:
        await db_session.refresh(e)
    return entries


@pytest.fixture
async def subject_with_works(
    db_session: AsyncSession, semester: Semester
) -> tuple[Subject, list[Work]]:
    """Create a subject with works that have deadlines."""
    subject = Subject(
        name="Математика",
        semester_id=semester.id,
    )
    db_session.add(subject)
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(subject)

    works = [
        Work(
            title="ДЗ №1",
            work_type="homework",
            subject_id=subject.id,
            deadline=datetime(2026, 3, 1, 23, 59, tzinfo=UTC),
        ),
        Work(
            title="Лаб №1",
            work_type="lab",
            subject_id=subject.id,
            deadline=datetime(2026, 3, 15, 23, 59, tzinfo=UTC),
        ),
        Work(
            title="Реферат",
            work_type="report",
            subject_id=subject.id,
            deadline=None,  # No deadline — should not appear
        ),
    ]
    for w in works:
        db_session.add(w)
    await db_session.flush()
    await db_session.commit()
    for w in works:
        await db_session.refresh(w)

    return subject, works


# ---- Token CRUD Tests ----


class TestTokenCRUD:
    """Tests for calendar feed token operations."""

    async def test_create_feed(self, db_session: AsyncSession, user: User) -> None:
        """Should create a new feed with a token."""
        feed = await cal_service.create_or_regenerate_feed(db_session, user.id)
        assert feed.user_id == user.id
        assert len(feed.token) > 0
        assert feed.last_accessed_at is None

    async def test_regenerate_feed(self, db_session: AsyncSession, user: User) -> None:
        """Should update token on second call."""
        feed1 = await cal_service.create_or_regenerate_feed(db_session, user.id)
        token1 = feed1.token

        feed2 = await cal_service.create_or_regenerate_feed(db_session, user.id)
        assert feed2.id == feed1.id
        assert feed2.token != token1

    async def test_get_by_token(self, db_session: AsyncSession, user: User) -> None:
        """Should find feed by its token."""
        feed = await cal_service.create_or_regenerate_feed(db_session, user.id)
        found = await cal_service.get_feed_by_token(db_session, feed.token)
        assert found is not None
        assert found.id == feed.id

    async def test_get_by_invalid_token(self, db_session: AsyncSession) -> None:
        """Should return None for non-existent token."""
        found = await cal_service.get_feed_by_token(db_session, "nonexistent")
        assert found is None

    async def test_revoke_feed(self, db_session: AsyncSession, user: User) -> None:
        """Should remove existing feed."""
        await cal_service.create_or_regenerate_feed(db_session, user.id)
        result = await cal_service.revoke_feed(db_session, user.id)
        assert result is True

        found = await cal_service.get_feed_by_user(db_session, user.id)
        assert found is None

    async def test_revoke_nonexistent(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should return False when no feed exists."""
        result = await cal_service.revoke_feed(db_session, user.id)
        assert result is False

    async def test_update_last_accessed(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should set last_accessed_at timestamp."""
        feed = await cal_service.create_or_regenerate_feed(db_session, user.id)
        assert feed.last_accessed_at is None

        await cal_service.update_last_accessed(db_session, feed)
        assert feed.last_accessed_at is not None


# ---- ICS Generation Tests ----


class TestICSGeneration:
    """Tests for ICS calendar generation."""

    async def test_valid_ics_output(
        self, db_session: AsyncSession, user: User, semester: Semester
    ) -> None:
        """Should produce valid iCalendar bytes."""
        ics = await cal_service.generate_ics(db_session, user.id)
        assert isinstance(ics, bytes)
        assert b"BEGIN:VCALENDAR" in ics
        assert b"END:VCALENDAR" in ics
        assert b"PRODID:-//StudyHelper//studyhelper1.ru//RU" in ics

    async def test_ics_with_schedule(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should include schedule entries as VEVENT."""
        ics = await cal_service.generate_ics(db_session, user.id)
        text = ics.decode("utf-8")
        assert "VEVENT" in text
        # All 5 entries should appear (no filters on this user)
        entry_count = text.count("schedule-")
        assert entry_count == 5

    async def test_ics_with_deadlines(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        subject_with_works: tuple[Subject, list[Work]],
    ) -> None:
        """Should include work deadlines as VEVENT with alarms."""
        ics = await cal_service.generate_ics(db_session, user.id)
        text = ics.decode("utf-8")
        # 2 works with deadlines
        deadline_count = text.count("deadline-")
        assert deadline_count == 2
        # Each deadline event should have 2 alarms (2 events x 2 alarms)
        assert text.count("BEGIN:VALARM") == 4

    async def test_ics_subgroup_filter(
        self,
        db_session: AsyncSession,
        user_with_prefs: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should filter entries by user's subgroup preference."""
        ics = await cal_service.generate_ics(db_session, user_with_prefs.id)
        text = ics.decode("utf-8")
        # User prefers subgroup 1: should see subgroup 1 and no-subgroup entries
        # Entries: Математика (no subgroup), Физика subgroup=1, PE teacher Иванов
        # Excluded: Физика subgroup=2, PE teacher Смирнов
        schedule_events = text.count("schedule-")
        assert schedule_events == 3  # math + physics_sg1 + PE_ivanov

    async def test_ics_pe_filter(
        self,
        db_session: AsyncSession,
        user_with_prefs: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should filter PE entries by preferred teacher."""
        ics = await cal_service.generate_ics(db_session, user_with_prefs.id)
        text = ics.decode("utf-8")
        # Should include Иванов, exclude Смирнов for PE
        assert "Иванов" in text
        assert "Смирнов" not in text

    async def test_ics_empty_semester(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should return valid but empty calendar when no current semester."""
        ics = await cal_service.generate_ics(db_session, user.id)
        assert b"BEGIN:VCALENDAR" in ics
        assert b"END:VCALENDAR" in ics

    async def test_ics_nonexistent_user(self, db_session: AsyncSession) -> None:
        """Should return empty calendar for non-existent user."""
        ics = await cal_service.generate_ics(db_session, 99999)
        assert b"BEGIN:VCALENDAR" in ics

    async def test_ics_contains_location(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should include location in schedule events."""
        ics = await cal_service.generate_ics(db_session, user.id)
        text = ics.decode("utf-8")
        assert "101" in text  # room
        assert "1" in text  # building reference

    async def test_ics_contains_refresh_interval(
        self, db_session: AsyncSession, user: User, semester: Semester
    ) -> None:
        """Should include REFRESH-INTERVAL property."""
        ics = await cal_service.generate_ics(db_session, user.id)
        assert b"REFRESH-INTERVAL" in ics


# ---- API Tests ----


class TestCalendarAPI:
    """Tests for calendar feed API endpoints."""

    async def test_status_inactive(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return inactive status when no feed exists."""
        response = await client.get("/api/v1/calendar/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["feed_url"] is None

    async def test_enable_feed(self, client: AsyncClient, auth_headers: dict) -> None:
        """Should create a feed and return URL."""
        response = await client.post("/api/v1/calendar/enable", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "feed_url" in data
        assert ".ics" in data["feed_url"]

    async def test_status_active(self, client: AsyncClient, auth_headers: dict) -> None:
        """Should return active status after enabling."""
        await client.post("/api/v1/calendar/enable", headers=auth_headers)
        response = await client.get("/api/v1/calendar/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert data["feed_url"] is not None

    async def test_disable_feed(self, client: AsyncClient, auth_headers: dict) -> None:
        """Should disable existing feed."""
        await client.post("/api/v1/calendar/enable", headers=auth_headers)
        response = await client.delete("/api/v1/calendar/disable", headers=auth_headers)
        assert response.status_code == 204

    async def test_disable_nonexistent(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return 404 when disabling non-existent feed."""
        response = await client.delete("/api/v1/calendar/disable", headers=auth_headers)
        assert response.status_code == 404

    async def test_public_feed_valid_token(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should serve .ics file for valid token."""
        enable_resp = await client.post("/api/v1/calendar/enable", headers=auth_headers)
        feed_url = enable_resp.json()["feed_url"]
        # Extract path from URL
        path = "/" + feed_url.split("/", 3)[-1]

        response = await client.get(path)
        assert response.status_code == 200
        assert "text/calendar" in response.headers["content-type"]
        assert b"BEGIN:VCALENDAR" in response.content

    async def test_public_feed_invalid_token(self, client: AsyncClient) -> None:
        """Should return 404 for invalid token."""
        response = await client.get("/api/v1/calendar/feed/nonexistent.ics")
        assert response.status_code == 404

    async def test_regenerate_changes_url(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return different URL on second enable call."""
        resp1 = await client.post("/api/v1/calendar/enable", headers=auth_headers)
        url1 = resp1.json()["feed_url"]

        resp2 = await client.post("/api/v1/calendar/enable", headers=auth_headers)
        url2 = resp2.json()["feed_url"]

        assert url1 != url2

    async def test_old_token_invalid_after_regenerate(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Old token should not work after regenerating."""
        resp1 = await client.post("/api/v1/calendar/enable", headers=auth_headers)
        old_url = resp1.json()["feed_url"]
        old_path = "/" + old_url.split("/", 3)[-1]

        # Regenerate
        await client.post("/api/v1/calendar/enable", headers=auth_headers)

        # Old token should 404
        response = await client.get(old_path)
        assert response.status_code == 404

    async def test_unauthenticated_status(self, client: AsyncClient) -> None:
        """Should require auth for status endpoint."""
        response = await client.get("/api/v1/calendar/status")
        assert response.status_code == 401

    async def test_feed_content_type(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return correct content type for .ics."""
        enable_resp = await client.post("/api/v1/calendar/enable", headers=auth_headers)
        feed_url = enable_resp.json()["feed_url"]
        path = "/" + feed_url.split("/", 3)[-1]

        response = await client.get(path)
        assert "text/calendar" in response.headers["content-type"]
        assert (
            response.headers.get("cache-control")
            == "no-cache, no-store, must-revalidate"
        )
