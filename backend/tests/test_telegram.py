"""Tests for Telegram service layer."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services import telegram as tg_service


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="tg_test@example.com",
        password_hash="fakehash",
        name="TG Test User",
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def user2(db_session: AsyncSession) -> User:
    """Create a second test user."""
    user = User(
        email="tg_test2@example.com",
        password_hash="fakehash2",
        name="TG Test User 2",
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestGenerateLinkCode:
    """Tests for generate_link_code."""

    async def test_creates_new_link(self, db_session: AsyncSession, user: User) -> None:
        """First call creates a new TelegramLink record."""
        link = await tg_service.generate_link_code(db_session, user.id)
        assert link.user_id == user.id
        assert link.link_code is not None
        assert len(link.link_code) == 6
        assert link.link_code_expires_at is not None
        assert link.telegram_id is None

    async def test_regenerates_code(self, db_session: AsyncSession, user: User) -> None:
        """Second call updates existing record with new code."""
        link1 = await tg_service.generate_link_code(db_session, user.id)
        code1 = link1.link_code

        link2 = await tg_service.generate_link_code(db_session, user.id)
        assert link2.id == link1.id
        assert link2.link_code != code1

    async def test_code_is_uppercase(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Link code should be uppercase."""
        link = await tg_service.generate_link_code(db_session, user.id)
        assert link.link_code == link.link_code.upper()  # type: ignore[union-attr]


class TestGetLinkByCode:
    """Tests for get_link_by_code."""

    async def test_finds_valid_code(self, db_session: AsyncSession, user: User) -> None:
        """Should find link with valid, non-expired code."""
        link = await tg_service.generate_link_code(db_session, user.id)
        found = await tg_service.get_link_by_code(db_session, link.link_code)  # type: ignore[arg-type]
        assert found is not None
        assert found.id == link.id

    async def test_returns_none_for_expired_code(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should return None for expired code."""
        link = await tg_service.generate_link_code(db_session, user.id)
        # Manually expire the code
        link.link_code_expires_at = datetime.now(UTC) - timedelta(minutes=1)
        await db_session.flush()
        await db_session.commit()

        found = await tg_service.get_link_by_code(db_session, link.link_code)  # type: ignore[arg-type]
        assert found is None

    async def test_returns_none_for_invalid_code(
        self, db_session: AsyncSession
    ) -> None:
        """Should return None for non-existent code."""
        found = await tg_service.get_link_by_code(db_session, "XXXXXX")
        assert found is None


class TestCompleteLink:
    """Tests for complete_link."""

    async def test_completes_link(self, db_session: AsyncSession, user: User) -> None:
        """Should set telegram_id and clear code."""
        link = await tg_service.generate_link_code(db_session, user.id)
        updated = await tg_service.complete_link(
            db_session, link, telegram_id=123456, telegram_username="testuser"
        )
        assert updated.telegram_id == 123456
        assert updated.telegram_username == "testuser"
        assert updated.link_code is None
        assert updated.link_code_expires_at is None
        assert updated.linked_at is not None


class TestUnlink:
    """Tests for unlink."""

    async def test_unlinks_existing(self, db_session: AsyncSession, user: User) -> None:
        """Should remove telegram link."""
        link = await tg_service.generate_link_code(db_session, user.id)
        await tg_service.complete_link(
            db_session, link, telegram_id=123456, telegram_username="test"
        )

        result = await tg_service.unlink(db_session, user.id)
        assert result is True

        found = await tg_service.get_link_by_user(db_session, user.id)
        assert found is None

    async def test_returns_false_when_not_linked(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should return False when no link exists."""
        result = await tg_service.unlink(db_session, user.id)
        assert result is False


class TestUpdateNotifications:
    """Tests for update_notifications."""

    async def test_updates_deadlines(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should toggle deadline notifications."""
        link = await tg_service.generate_link_code(db_session, user.id)
        await tg_service.complete_link(
            db_session, link, telegram_id=123456, telegram_username="test"
        )

        updated = await tg_service.update_notifications(
            db_session, user.id, notify_deadlines=False
        )
        assert updated is not None
        assert updated.notify_deadlines is False
        assert updated.morning_summary is True

    async def test_updates_morning_summary(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should toggle morning summary."""
        link = await tg_service.generate_link_code(db_session, user.id)
        await tg_service.complete_link(
            db_session, link, telegram_id=123456, telegram_username="test"
        )

        updated = await tg_service.update_notifications(
            db_session, user.id, morning_summary=False
        )
        assert updated is not None
        assert updated.morning_summary is False

    async def test_returns_none_when_not_linked(
        self, db_session: AsyncSession, user: User
    ) -> None:
        """Should return None when user has no link."""
        result = await tg_service.update_notifications(
            db_session, user.id, notify_deadlines=False
        )
        assert result is None


class TestGetLinkedUsers:
    """Tests for get_all_linked_users and filtered variants."""

    async def test_get_all_linked(
        self, db_session: AsyncSession, user: User, user2: User
    ) -> None:
        """Should return only linked users."""
        # User1: linked
        link1 = await tg_service.generate_link_code(db_session, user.id)
        await tg_service.complete_link(
            db_session, link1, telegram_id=111, telegram_username="u1"
        )
        # User2: code generated but not linked
        await tg_service.generate_link_code(db_session, user2.id)

        linked = await tg_service.get_all_linked_users(db_session)
        assert len(linked) == 1
        assert linked[0].telegram_id == 111

    async def test_get_morning_summary_users(
        self, db_session: AsyncSession, user: User, user2: User
    ) -> None:
        """Should filter by morning_summary preference."""
        link1 = await tg_service.generate_link_code(db_session, user.id)
        await tg_service.complete_link(
            db_session, link1, telegram_id=111, telegram_username="u1"
        )

        link2 = await tg_service.generate_link_code(db_session, user2.id)
        await tg_service.complete_link(
            db_session, link2, telegram_id=222, telegram_username="u2"
        )
        await tg_service.update_notifications(
            db_session, user2.id, morning_summary=False
        )

        users = await tg_service.get_users_with_morning_summary(db_session)
        assert len(users) == 1
        assert users[0].telegram_id == 111

    async def test_get_deadline_alert_users(
        self, db_session: AsyncSession, user: User, user2: User
    ) -> None:
        """Should filter by notify_deadlines preference."""
        link1 = await tg_service.generate_link_code(db_session, user.id)
        await tg_service.complete_link(
            db_session, link1, telegram_id=111, telegram_username="u1"
        )
        await tg_service.update_notifications(
            db_session, user.id, notify_deadlines=False
        )

        link2 = await tg_service.generate_link_code(db_session, user2.id)
        await tg_service.complete_link(
            db_session, link2, telegram_id=222, telegram_username="u2"
        )

        users = await tg_service.get_users_with_deadline_alerts(db_session)
        assert len(users) == 1
        assert users[0].telegram_id == 222


class TestHiddenSubjectsFiltering:
    """Integration tests for hidden_subjects filtering in Telegram bot."""

    @pytest.fixture
    async def semester(self, db_session: AsyncSession):
        """Create a test semester."""
        from src.models.semester import Semester

        semester = Semester(
            number=1,
            year_start=2024,
            year_end=2025,
            name="1 семестр 2024-2025",
            start_date=datetime(2024, 9, 1).date(),
            end_date=datetime(2025, 1, 31).date(),
        )
        db_session.add(semester)
        await db_session.commit()
        await db_session.refresh(semester)
        return semester

    @pytest.fixture
    async def math_subject(self, db_session: AsyncSession, semester):
        """Create a math subject."""
        from src.models.subject import Subject

        subject = Subject(
            name="Математика",
            short_name="Матем",
            semester_id=semester.id,
        )
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)
        return subject

    @pytest.fixture
    async def physics_subject(self, db_session: AsyncSession, semester):
        """Create a physics subject."""
        from src.models.subject import Subject

        subject = Subject(
            name="Физика",
            short_name="Физ",
            semester_id=semester.id,
        )
        db_session.add(subject)
        await db_session.commit()
        await db_session.refresh(subject)
        return subject

    @pytest.fixture
    async def schedule_entries(
        self, db_session: AsyncSession, math_subject, physics_subject
    ):
        """Create schedule entries for today."""
        from datetime import date, time

        from src.models.schedule import ScheduleEntry

        today = date.today()
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

    @pytest.fixture
    async def work(self, db_session: AsyncSession, math_subject):
        """Create a work for math subject."""
        from src.models.work import Work

        work = Work(
            title="Lab 1",
            work_type="lab",
            subject_id=math_subject.id,
            deadline=datetime.now(UTC) + timedelta(hours=12),
        )
        db_session.add(work)
        await db_session.commit()
        await db_session.refresh(work)
        return work

    async def test_filtered_day_schedule_with_hidden_subjects(
        self,
        db_session: AsyncSession,
        user: User,
        math_subject,
        schedule_entries,
    ):
        """Test that get_filtered_day_schedule filters hidden subjects."""
        from src.telegram.schedule_utils import get_filtered_day_schedule

        # Hide math subject completely
        user.hidden_subjects = {str(math_subject.id): None}
        await db_session.commit()

        result = await get_filtered_day_schedule(db_session, user)

        # Should only have physics entry
        assert len(result.entries) == 1
        assert result.entries[0].subject_name == "Физика"

    async def test_filter_works_by_hidden_subjects(
        self,
        db_session: AsyncSession,
        user: User,
        math_subject,
        work,
    ):
        """Test that filter_works_by_hidden_subjects filters fully hidden subjects."""
        from src.telegram.schedule_utils import filter_works_by_hidden_subjects
        from src.utils.schedule_filters import resolve_hidden_subjects

        # Hide math subject completely
        user.hidden_subjects = {str(math_subject.id): None}
        await db_session.commit()

        hidden_config = await resolve_hidden_subjects(db_session, user)
        result = filter_works_by_hidden_subjects([work], hidden_config)

        # Work should be filtered out
        assert len(result) == 0

    async def test_per_type_hiding_does_not_filter_works(
        self,
        db_session: AsyncSession,
        user: User,
        math_subject,
        work,
    ):
        """Test that per-type hiding does NOT filter works."""
        from src.telegram.schedule_utils import filter_works_by_hidden_subjects
        from src.utils.schedule_filters import resolve_hidden_subjects

        # Hide only math lab lessons (per-type)
        user.hidden_subjects = {str(math_subject.id): ["lab"]}
        await db_session.commit()

        hidden_config = await resolve_hidden_subjects(db_session, user)
        result = filter_works_by_hidden_subjects([work], hidden_config)

        # Work should NOT be filtered (per-type hiding doesn't apply to works)
        assert len(result) == 1
        assert result[0].title == "Lab 1"
