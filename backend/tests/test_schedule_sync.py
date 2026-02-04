"""Tests for schedule synchronization functionality."""

from datetime import date, time
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from src.parser.omsu_parser import ParseResult
from src.schemas.schedule import DayOfWeek, LessonType, ScheduleEntryCreate


def create_mock_parse_result(
    entries_count: int = 3,
    content_hash: str = "abc123def456",
) -> ParseResult:
    """Create a mock ParseResult for testing.

    Args:
        entries_count: Number of entries to create.
        content_hash: Content hash to use.

    Returns:
        ParseResult with mock data.
    """
    entries = []
    raw_data = []

    for i in range(entries_count):
        entry = ScheduleEntryCreate(
            day_of_week=DayOfWeek((i % 5) + 1),  # Monday to Friday
            start_time=time(8 + i, 0),
            end_time=time(9 + i, 30),
            subject_name=f"Subject {i + 1}",
            lesson_type=LessonType.LECTURE,
            teacher_name=f"Teacher {i + 1}",
            room=f"10{i}",
            building="2",
        )
        entries.append(entry)
        raw_data.append(
            {
                "day_of_week": entry.day_of_week.value,
                "start_time": str(entry.start_time),
                "end_time": str(entry.end_time),
                "subject_name": entry.subject_name,
                "lesson_type": entry.lesson_type.value,
                "teacher_name": entry.teacher_name,
                "room": entry.room,
                "building": entry.building,
            }
        )

    return ParseResult(
        entries=entries,
        raw_data=raw_data,
        content_hash=content_hash,
        source_url="https://example.com/schedule",
        parsed_date=date.today(),
    )


@pytest.fixture
def mock_parse_result():
    """Fixture for mock parse result."""
    return create_mock_parse_result()


@pytest.fixture
def mock_parse_result_changed():
    """Fixture for changed mock parse result."""
    return create_mock_parse_result(
        entries_count=5,
        content_hash="new_hash_xyz789",
    )


class TestScheduleRefreshEndpoint:
    """Tests for POST /api/v1/schedule/refresh endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_schedule_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_parse_result: ParseResult,
    ):
        """Test successful schedule refresh."""
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            response = await client.post(
                "/api/v1/schedule/refresh",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["changed"] is True
            assert data["entries_count"] == 3

    @pytest.mark.asyncio
    async def test_refresh_schedule_unchanged(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_parse_result: ParseResult,
    ):
        """Test refresh when schedule unchanged (same hash)."""
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            # First refresh
            response1 = await client.post(
                "/api/v1/schedule/refresh",
                headers=auth_headers,
            )
            assert response1.status_code == 200
            assert response1.json()["changed"] is True

            # Second refresh with same hash
            response2 = await client.post(
                "/api/v1/schedule/refresh",
                headers=auth_headers,
            )
            assert response2.status_code == 200
            data = response2.json()
            assert data["success"] is True
            assert data["changed"] is False
            assert data["message"] == "Schedule unchanged"

    @pytest.mark.asyncio
    async def test_refresh_schedule_force(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_parse_result: ParseResult,
    ):
        """Test force refresh updates even with same hash."""
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            # First refresh
            await client.post(
                "/api/v1/schedule/refresh",
                headers=auth_headers,
            )

            # Force refresh with same hash
            response = await client.post(
                "/api/v1/schedule/refresh?force=true",
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["changed"] is True

    @pytest.mark.asyncio
    async def test_refresh_schedule_unauthorized(self, client: AsyncClient):
        """Test refresh without authentication returns 401."""
        response = await client.post("/api/v1/schedule/refresh")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_schedule_parser_error(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test refresh when parser raises error."""
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            side_effect=Exception("Parser failed"),
        ):
            response = await client.post(
                "/api/v1/schedule/refresh",
                headers=auth_headers,
            )

            assert response.status_code == 500
            assert "Parser failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_refresh_schedule_no_entries(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test refresh when parser returns no entries."""
        empty_result = ParseResult(
            entries=[],
            raw_data=[],
            content_hash="empty_hash",
            source_url="https://example.com/schedule",
            parsed_date=date.today(),
        )

        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=empty_result,
        ):
            response = await client.post(
                "/api/v1/schedule/refresh",
                headers=auth_headers,
            )

            assert response.status_code == 500
            assert "No entries parsed" in response.json()["detail"]


class TestScheduleSyncService:
    """Tests for schedule sync service functions."""

    @pytest.mark.asyncio
    async def test_sync_schedule_creates_entries(
        self,
        db_session,
        mock_parse_result: ParseResult,
    ):
        """Test sync_schedule creates entries in database."""
        from sqlalchemy import select

        from src.models.schedule import ScheduleEntry
        from src.services import schedule as schedule_service

        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            result = await schedule_service.sync_schedule(db_session)

            assert result["success"] is True
            assert result["changed"] is True
            assert result["entries_count"] == 3

            # Verify entries in database
            query = select(ScheduleEntry)
            db_result = await db_session.execute(query)
            entries = db_result.scalars().all()
            assert len(entries) == 3

    @pytest.mark.asyncio
    async def test_sync_schedule_creates_snapshot(
        self,
        db_session,
        mock_parse_result: ParseResult,
    ):
        """Test sync_schedule creates snapshot in database."""
        from src.services import schedule as schedule_service

        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            result = await schedule_service.sync_schedule(db_session)

            assert result["success"] is True

            # Verify snapshot created
            snapshot = await schedule_service.get_latest_snapshot(db_session)
            assert snapshot is not None
            assert snapshot.content_hash == mock_parse_result.content_hash
            assert snapshot.entries_count == 3

    @pytest.mark.asyncio
    async def test_sync_schedule_clears_old_entries(
        self,
        db_session,
        mock_parse_result: ParseResult,
        mock_parse_result_changed: ParseResult,
    ):
        """Test sync_schedule clears old entries on update."""
        from sqlalchemy import select

        from src.models.schedule import ScheduleEntry
        from src.services import schedule as schedule_service

        # First sync
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            await schedule_service.sync_schedule(db_session)

        # Second sync with different data
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result_changed,
        ):
            result = await schedule_service.sync_schedule(db_session)

            assert result["success"] is True
            assert result["entries_count"] == 5

            # Verify only new entries exist
            query = select(ScheduleEntry)
            db_result = await db_session.execute(query)
            entries = db_result.scalars().all()
            assert len(entries) == 5

    @pytest.mark.asyncio
    async def test_sync_schedule_unchanged_no_update(
        self,
        db_session,
        mock_parse_result: ParseResult,
    ):
        """Test sync_schedule skips update when hash unchanged."""
        from src.services import schedule as schedule_service

        # First sync
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            await schedule_service.sync_schedule(db_session)

        # Second sync with same hash
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            result = await schedule_service.sync_schedule(db_session)

            assert result["success"] is True
            assert result["changed"] is False

    @pytest.mark.asyncio
    async def test_sync_schedule_force_updates(
        self,
        db_session,
        mock_parse_result: ParseResult,
    ):
        """Test sync_schedule with force=True updates despite same hash."""
        from src.services import schedule as schedule_service

        # First sync
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            await schedule_service.sync_schedule(db_session)

        # Force sync with same hash
        with patch(
            "src.services.schedule.parse_schedule",
            new_callable=AsyncMock,
            return_value=mock_parse_result,
        ):
            result = await schedule_service.sync_schedule(db_session, force=True)

            assert result["success"] is True
            assert result["changed"] is True
