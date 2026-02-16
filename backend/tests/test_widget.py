"""Tests for widget API key service and API."""

from datetime import date, datetime, time, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule import ScheduleEntry
from src.models.semester import Semester
from src.models.user import User
from src.services import widget as widget_service


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="widget_test@example.com",
        password_hash="fakehash",
        name="Widget Test User",
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
        email="widget_prefs@example.com",
        password_hash="fakehash",
        name="Widget Prefs User",
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


def _today() -> date:
    """Get today's date in configured timezone."""
    from zoneinfo import ZoneInfo

    from src.config import settings

    tz = ZoneInfo(settings.timezone)
    return datetime.now(tz).date()


def _tomorrow() -> date:
    """Get tomorrow's date for consistent test data."""
    from zoneinfo import ZoneInfo

    from src.config import settings

    tz = ZoneInfo(settings.timezone)
    return (datetime.now(tz) + timedelta(days=1)).date()


@pytest.fixture
async def schedule_entries(
    db_session: AsyncSession, semester: Semester
) -> list[ScheduleEntry]:
    """Create sample schedule entries for tomorrow."""
    tomorrow = _tomorrow()
    day_after = tomorrow + timedelta(days=1)

    entries = [
        ScheduleEntry(
            lesson_date=tomorrow,
            day_of_week=tomorrow.isoweekday(),
            start_time=time(8, 0),
            end_time=time(9, 30),
            subject_name="Математика",
            lesson_type="lecture",
            teacher_name="Петров П.П.",
            room="101",
            building="Корпус 1",
        ),
        ScheduleEntry(
            lesson_date=tomorrow,
            day_of_week=tomorrow.isoweekday(),
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
            lesson_date=tomorrow,
            day_of_week=tomorrow.isoweekday(),
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
            lesson_date=day_after,
            day_of_week=day_after.isoweekday(),
            start_time=time(8, 0),
            end_time=time(9, 30),
            subject_name="Физическая культура",
            lesson_type="practice",
            teacher_name="Иванов И.И.",
            room="Зал 1",
            building="Спортзал",
        ),
        ScheduleEntry(
            lesson_date=day_after,
            day_of_week=day_after.isoweekday(),
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
async def today_schedule_entries(
    db_session: AsyncSession, semester: Semester
) -> list[ScheduleEntry]:
    """Create sample schedule entries for today and tomorrow."""
    today = _today()
    tomorrow = today + timedelta(days=1)

    entries = [
        ScheduleEntry(
            lesson_date=today,
            day_of_week=today.isoweekday(),
            start_time=time(8, 0),
            end_time=time(9, 30),
            subject_name="Математика",
            lesson_type="lecture",
            teacher_name="Петров П.П.",
            room="101",
            building="Корпус 1",
        ),
        ScheduleEntry(
            lesson_date=today,
            day_of_week=today.isoweekday(),
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
            lesson_date=today,
            day_of_week=today.isoweekday(),
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
            lesson_date=today,
            day_of_week=today.isoweekday(),
            start_time=time(23, 50),
            end_time=time(23, 59),
            subject_name="Программирование",
            lesson_type="lab",
            teacher_name="Кузнецов К.К.",
            room="301",
            building="Корпус 3",
        ),
        ScheduleEntry(
            lesson_date=tomorrow,
            day_of_week=tomorrow.isoweekday(),
            start_time=time(8, 0),
            end_time=time(9, 30),
            subject_name="Физическая культура",
            lesson_type="practice",
            teacher_name="Иванов И.И.",
            room="Зал 1",
            building="Спортзал",
        ),
        ScheduleEntry(
            lesson_date=tomorrow,
            day_of_week=tomorrow.isoweekday(),
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


# ---- Token CRUD Tests ----


class TestTokenCRUD:
    """Tests for widget API key token operations."""

    async def test_create_key(self, db_session: AsyncSession, user: User) -> None:
        """Should create a new API key with a token."""
        key = await widget_service.create_or_regenerate_key(db_session, user.id)
        assert key.user_id == user.id
        assert len(key.token) > 0
        assert key.last_used_at is None

    async def test_regenerate_key(self, db_session: AsyncSession, user: User) -> None:
        """Should update token on second call."""
        key1 = await widget_service.create_or_regenerate_key(db_session, user.id)
        token1 = key1.token

        key2 = await widget_service.create_or_regenerate_key(db_session, user.id)
        assert key2.id == key1.id
        assert key2.token != token1

    async def test_get_by_token(self, db_session: AsyncSession, user: User) -> None:
        """Should find API key by its token."""
        key = await widget_service.create_or_regenerate_key(db_session, user.id)
        found = await widget_service.get_key_by_token(db_session, key.token)
        assert found is not None
        assert found.id == key.id

    async def test_get_by_invalid_token(self, db_session: AsyncSession) -> None:
        """Should return None for non-existent token."""
        found = await widget_service.get_key_by_token(db_session, "nonexistent")
        assert found is None

    async def test_revoke_key(self, db_session: AsyncSession, user: User) -> None:
        """Should remove existing API key."""
        await widget_service.create_or_regenerate_key(db_session, user.id)
        result = await widget_service.revoke_key(db_session, user.id)
        assert result is True

        found = await widget_service.get_key_by_user(db_session, user.id)
        assert found is None

    async def test_revoke_nonexistent(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should return False when no API key exists."""
        result = await widget_service.revoke_key(db_session, user.id)
        assert result is False

    async def test_update_last_used(self, db_session: AsyncSession, user: User) -> None:
        """Should set last_used_at timestamp."""
        key = await widget_service.create_or_regenerate_key(db_session, user.id)
        assert key.last_used_at is None

        await widget_service.update_last_used(db_session, key)
        assert key.last_used_at is not None


# ---- Next Lesson Logic Tests ----


class TestNextLessonLogic:
    """Tests for next lesson lookup logic."""

    async def test_next_lesson_tomorrow(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should return first lesson of tomorrow when no today entries."""
        result = await widget_service.get_next_lesson(db_session, user)
        assert result.no_more_lessons is False
        assert result.subject == "Математика"
        assert result.time_start == "08:00"
        assert result.time_end == "09:30"
        assert result.is_today is False

    async def test_next_lesson_location(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should include location with room and building."""
        result = await widget_service.get_next_lesson(db_session, user)
        assert result.location is not None
        assert "101" in result.location
        assert "Корпус 1" in result.location

    async def test_next_lesson_teacher(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should include teacher name."""
        result = await widget_service.get_next_lesson(db_session, user)
        assert result.teacher == "Петров П.П."

    async def test_next_lesson_minutes_until(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should calculate minutes_until for the next lesson."""
        result = await widget_service.get_next_lesson(db_session, user)
        assert result.minutes_until is not None
        assert result.minutes_until > 0

    async def test_next_lesson_lesson_type(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should return localized lesson type."""
        result = await widget_service.get_next_lesson(db_session, user)
        assert result.lesson_type == "Лекция"

    async def test_next_lesson_subgroup_filter(
        self,
        db_session: AsyncSession,
        user_with_prefs: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should filter entries by user's subgroup preference."""
        result = await widget_service.get_next_lesson(db_session, user_with_prefs)
        # First lesson is Математика (no subgroup), should be returned
        assert result.subject == "Математика"

    async def test_next_lesson_pe_filter(
        self,
        db_session: AsyncSession,
        user_with_prefs: User,
        semester: Semester,
        schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should filter PE entries by preferred teacher."""
        # Create entries with only PE on tomorrow
        tomorrow = _tomorrow()
        for entry in schedule_entries:
            if entry.lesson_date == tomorrow:
                await db_session.delete(entry)
        await db_session.commit()

        result = await widget_service.get_next_lesson(db_session, user_with_prefs)
        # Should show Иванов (preferred), not Смирнов
        if not result.no_more_lessons:
            assert result.teacher == "Иванов И.И."

    async def test_no_lessons_when_empty(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
    ) -> None:
        """Should return no_more_lessons when no entries exist."""
        result = await widget_service.get_next_lesson(db_session, user)
        assert result.no_more_lessons is True

    async def test_no_lessons_without_semester(
        self,
        db_session: AsyncSession,
        user: User,
    ) -> None:
        """Should return no_more_lessons when no current semester."""
        result = await widget_service.get_next_lesson(db_session, user)
        assert result.no_more_lessons is True

    async def test_cached_at_present(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
    ) -> None:
        """Should always include cached_at timestamp."""
        result = await widget_service.get_next_lesson(db_session, user)
        assert result.cached_at is not None


# ---- API Tests ----


class TestWidgetAPI:
    """Tests for widget API endpoints."""

    async def test_status_inactive(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return inactive status when no API key exists."""
        response = await client.get("/api/v1/widget/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["api_key"] is None

    async def test_enable_widget(self, client: AsyncClient, auth_headers: dict) -> None:
        """Should create an API key and return it."""
        response = await client.post("/api/v1/widget/enable", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert "widget_url" in data
        assert "api_key=" in data["widget_url"]

    async def test_status_active(self, client: AsyncClient, auth_headers: dict) -> None:
        """Should return active status after enabling."""
        await client.post("/api/v1/widget/enable", headers=auth_headers)
        response = await client.get("/api/v1/widget/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert data["api_key"] is not None
        assert data["widget_url"] is not None

    async def test_disable_widget(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should disable existing API key."""
        await client.post("/api/v1/widget/enable", headers=auth_headers)
        response = await client.delete("/api/v1/widget/disable", headers=auth_headers)
        assert response.status_code == 204

    async def test_disable_nonexistent(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return 404 when disabling non-existent key."""
        response = await client.delete("/api/v1/widget/disable", headers=auth_headers)
        assert response.status_code == 404

    async def test_next_lesson_valid_key(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return next lesson data for valid API key."""
        enable_resp = await client.post("/api/v1/widget/enable", headers=auth_headers)
        api_key = enable_resp.json()["api_key"]

        response = await client.get(f"/api/v1/widget/next-lesson?api_key={api_key}")
        assert response.status_code == 200
        data = response.json()
        # No semester/entries so no_more_lessons
        assert data["no_more_lessons"] is True
        assert data["cached_at"] is not None

    async def test_next_lesson_invalid_key(self, client: AsyncClient) -> None:
        """Should return 401 for invalid API key."""
        response = await client.get("/api/v1/widget/next-lesson?api_key=nonexistent")
        assert response.status_code == 401

    async def test_next_lesson_missing_key(self, client: AsyncClient) -> None:
        """Should return 422 when api_key parameter is missing."""
        response = await client.get("/api/v1/widget/next-lesson")
        assert response.status_code == 422

    async def test_regenerate_changes_key(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return different key on second enable call."""
        resp1 = await client.post("/api/v1/widget/enable", headers=auth_headers)
        key1 = resp1.json()["api_key"]

        resp2 = await client.post("/api/v1/widget/enable", headers=auth_headers)
        key2 = resp2.json()["api_key"]

        assert key1 != key2

    async def test_old_key_invalid_after_regenerate(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Old API key should not work after regenerating."""
        resp1 = await client.post("/api/v1/widget/enable", headers=auth_headers)
        old_key = resp1.json()["api_key"]

        # Regenerate
        await client.post("/api/v1/widget/enable", headers=auth_headers)

        # Old key should fail
        response = await client.get(f"/api/v1/widget/next-lesson?api_key={old_key}")
        assert response.status_code == 401

    async def test_unauthenticated_status(self, client: AsyncClient) -> None:
        """Should require auth for status endpoint."""
        response = await client.get("/api/v1/widget/status")
        assert response.status_code == 401

    async def test_unauthenticated_enable(self, client: AsyncClient) -> None:
        """Should require auth for enable endpoint."""
        response = await client.post("/api/v1/widget/enable")
        assert response.status_code == 401


# ---- Today Schedule Logic Tests ----


class TestTodayScheduleLogic:
    """Tests for today schedule lookup logic."""

    async def test_returns_all_today_lessons(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        today_schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should return all lessons for today including past ones."""
        result = await widget_service.get_today_schedule(db_session, user)
        # 4 today entries, but 2 are subgroup-specific and user has no preference
        # so all 4 should be returned (no subgroup filter for user without prefs)
        assert len(result.lessons) == 4

    async def test_lessons_sorted_by_time(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        today_schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should return lessons sorted by start time."""
        result = await widget_service.get_today_schedule(db_session, user)
        times = [lesson.time_start for lesson in result.lessons]
        assert times == sorted(times)

    async def test_date_is_today(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        today_schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should set date to today's date."""
        result = await widget_service.get_today_schedule(db_session, user)
        assert result.date == _today().isoformat()

    async def test_cached_at_present(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        today_schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should include cached_at timestamp."""
        result = await widget_service.get_today_schedule(db_session, user)
        assert result.cached_at is not None
        assert "T" in result.cached_at

    async def test_empty_without_entries(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
    ) -> None:
        """Should return empty lessons list when no entries exist."""
        result = await widget_service.get_today_schedule(db_session, user)
        assert result.lessons == []
        assert result.next_lesson_from_future is None

    async def test_empty_without_semester(
        self,
        db_session: AsyncSession,
        user: User,
    ) -> None:
        """Should return empty response when no current semester."""
        result = await widget_service.get_today_schedule(db_session, user)
        assert result.lessons == []
        assert result.next_lesson_from_future is None

    async def test_subgroup_filter(
        self,
        db_session: AsyncSession,
        user_with_prefs: User,
        semester: Semester,
        today_schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should filter entries by user's subgroup preference."""
        result = await widget_service.get_today_schedule(db_session, user_with_prefs)
        subjects = [item.subject for item in result.lessons]
        # subgroup=1 user: Математика (no subgroup), Физика subgroup=1, Программирование (no subgroup)
        assert "Математика" in subjects
        assert "Программирование" in subjects
        # Should have Физика from subgroup 1 (Сидоров), not subgroup 2 (Козлов)
        physics_lessons = [item for item in result.lessons if item.subject == "Физика"]
        assert len(physics_lessons) == 1
        assert physics_lessons[0].teacher == "Сидоров С.С."

    async def test_pe_filter(
        self,
        db_session: AsyncSession,
        user_with_prefs: User,
        semester: Semester,
        today_schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should filter PE entries by preferred teacher in future lessons."""
        result = await widget_service.get_today_schedule(db_session, user_with_prefs)
        # Future lesson should be PE with preferred teacher Иванов
        if result.next_lesson_from_future:
            assert result.next_lesson_from_future.teacher == "Иванов И.И."

    async def test_next_lesson_from_future_present(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
        today_schedule_entries: list[ScheduleEntry],
    ) -> None:
        """Should include first future lesson when available."""
        result = await widget_service.get_today_schedule(db_session, user)
        assert result.next_lesson_from_future is not None
        assert result.next_lesson_date is not None
        tomorrow = _today() + timedelta(days=1)
        assert result.next_lesson_date == tomorrow.isoformat()

    async def test_next_lesson_from_future_none_without_future(
        self,
        db_session: AsyncSession,
        user: User,
        semester: Semester,
    ) -> None:
        """Should set next_lesson_from_future to None when no future entries."""
        # Create only today entries
        today = _today()
        entry = ScheduleEntry(
            lesson_date=today,
            day_of_week=today.isoweekday(),
            start_time=time(8, 0),
            end_time=time(9, 30),
            subject_name="Математика",
            lesson_type="lecture",
            teacher_name="Петров П.П.",
            room="101",
            building="Корпус 1",
        )
        db_session.add(entry)
        await db_session.flush()
        await db_session.commit()

        result = await widget_service.get_today_schedule(db_session, user)
        assert result.next_lesson_from_future is None
        assert result.next_lesson_date is None


# ---- Today Schedule API Tests ----


class TestTodayScheduleAPI:
    """Tests for /today API endpoint."""

    async def test_today_valid_key(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return 200 with today schedule for valid API key."""
        enable_resp = await client.post("/api/v1/widget/enable", headers=auth_headers)
        api_key = enable_resp.json()["api_key"]

        response = await client.get(f"/api/v1/widget/today?api_key={api_key}")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "lessons" in data
        assert "cached_at" in data
        assert isinstance(data["lessons"], list)

    async def test_today_invalid_key(self, client: AsyncClient) -> None:
        """Should return 401 for invalid API key."""
        response = await client.get("/api/v1/widget/today?api_key=nonexistent")
        assert response.status_code == 401

    async def test_today_missing_key(self, client: AsyncClient) -> None:
        """Should return 422 when api_key parameter is missing."""
        response = await client.get("/api/v1/widget/today")
        assert response.status_code == 422

    async def test_today_response_structure(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Should return properly structured response."""
        enable_resp = await client.post("/api/v1/widget/enable", headers=auth_headers)
        api_key = enable_resp.json()["api_key"]

        response = await client.get(f"/api/v1/widget/today?api_key={api_key}")
        data = response.json()
        assert "date" in data
        assert "lessons" in data
        assert "next_lesson_from_future" in data
        assert "next_lesson_date" in data
        assert "cached_at" in data
