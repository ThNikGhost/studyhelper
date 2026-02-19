"""Tests for schedule entry filtering utilities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.utils.schedule_filters import (
    filter_entries_by_user_prefs,
    resolve_hidden_subjects,
)


def _make_entry(
    *,
    subject_id: int | None = None,
    subject_name: str = "Математика",
    teacher_name: str | None = None,
    subgroup: int | None = None,
    lesson_type: str = "lecture",
) -> MagicMock:
    """Create a mock ScheduleEntry."""
    entry = MagicMock()
    entry.subject_id = subject_id
    entry.subject_name = subject_name
    entry.teacher_name = teacher_name
    entry.subgroup = subgroup
    entry.lesson_type = lesson_type
    return entry


def _make_user(
    *,
    preferred_subgroup: int | None = None,
    preferred_pe_teacher: str | None = None,
    hidden_subjects: dict[str, list[str] | None] | None = None,
) -> MagicMock:
    """Create a mock User."""
    user = MagicMock()
    user.preferred_subgroup = preferred_subgroup
    user.preferred_pe_teacher = preferred_pe_teacher
    user.hidden_subjects = hidden_subjects
    return user


class TestHiddenSubjectsFilter:
    """Tests for hidden subjects filtering in filter_entries_by_user_prefs."""

    def test_no_hidden_config_passes_all(self):
        """All entries pass when hidden_subjects is None."""
        entries = [
            _make_entry(subject_name="Математика"),
            _make_entry(subject_name="Физика"),
        ]
        user = _make_user(hidden_subjects=None)

        result = filter_entries_by_user_prefs(entries, user, hidden_subjects=None)

        assert len(result) == 2

    def test_empty_hidden_config_passes_all(self):
        """All entries pass when hidden_subjects is empty dict."""
        entries = [
            _make_entry(subject_name="Математика"),
            _make_entry(subject_name="Физика"),
        ]
        user = _make_user(hidden_subjects={})

        result = filter_entries_by_user_prefs(entries, user, hidden_subjects={})

        assert len(result) == 2

    def test_fully_hidden_subject_filters_all_types(self):
        """Subject with null types is fully hidden (all lesson types)."""
        entries = [
            _make_entry(subject_name="Математика", lesson_type="lecture"),
            _make_entry(subject_name="Математика", lesson_type="practice"),
            _make_entry(subject_name="Физика", lesson_type="lecture"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subjects={"Математика": None}
        )

        assert len(result) == 1
        assert result[0].subject_name == "Физика"

    def test_per_type_hidden_filters_only_specified_types(self):
        """Subject with specific types hides only those lesson types."""
        entries = [
            _make_entry(subject_name="Математика", lesson_type="lecture"),
            _make_entry(subject_name="Математика", lesson_type="lab"),
            _make_entry(subject_name="Математика", lesson_type="practice"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subjects={"Математика": {"lab"}}
        )

        assert len(result) == 2
        types = [e.lesson_type for e in result]
        assert "lecture" in types
        assert "practice" in types
        assert "lab" not in types

    def test_per_type_hidden_multiple_types(self):
        """Multiple lesson types can be hidden for one subject."""
        entries = [
            _make_entry(subject_name="Физика", lesson_type="lecture"),
            _make_entry(subject_name="Физика", lesson_type="lab"),
            _make_entry(subject_name="Физика", lesson_type="practice"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subjects={"Физика": {"lab", "practice"}}
        )

        assert len(result) == 1
        assert result[0].lesson_type == "lecture"

    def test_entry_with_null_subject_name_not_filtered(self):
        """Entries with subject_name=None are never hidden."""
        entries = [
            _make_entry(subject_name=None),
            _make_entry(subject_name="Математика"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subjects={"Математика": None}
        )

        assert len(result) == 1
        assert result[0].subject_name is None

    def test_multiple_hidden_subjects_mixed(self):
        """Multiple subjects: one fully hidden, one per-type."""
        entries = [
            _make_entry(subject_name="Математика", lesson_type="lecture"),
            _make_entry(subject_name="Физика", lesson_type="lecture"),
            _make_entry(subject_name="Физика", lesson_type="lab"),
            _make_entry(subject_name="Химия", lesson_type="lecture"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(
            entries,
            user,
            hidden_subjects={"Математика": None, "Физика": {"lab"}},
        )

        assert len(result) == 2
        names_types = [(e.subject_name, e.lesson_type) for e in result]
        assert ("Физика", "lecture") in names_types
        assert ("Химия", "lecture") in names_types

    def test_hidden_subjects_combined_with_subgroup_filter(self):
        """Hidden subjects filter works alongside subgroup filter."""
        entries = [
            _make_entry(subject_name="Математика", subgroup=1),
            _make_entry(subject_name="Математика", subgroup=2),
            _make_entry(subject_name="Физика", subgroup=1),
        ]
        user = _make_user(preferred_subgroup=1)

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subjects={"Физика": None}
        )

        # subject_name="Математика" subgroup=2 filtered by subgroup
        # subject_name="Физика" subgroup=1 filtered by hidden
        assert len(result) == 1
        assert result[0].subject_name == "Математика"
        assert result[0].subgroup == 1

    def test_no_hidden_param_passes_all(self):
        """All entries pass when hidden_subjects param is not provided."""
        entries = [
            _make_entry(subject_name="Математика"),
            _make_entry(subject_name="Физика"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(entries, user)

        assert len(result) == 2


class TestResolveHiddenSubjects:
    """Tests for resolve_hidden_subjects."""

    @pytest.mark.asyncio
    async def test_empty_hidden_subjects_returns_empty_dict(self):
        """Returns empty dict when user has no hidden subjects."""
        db = AsyncMock()
        user = _make_user(hidden_subjects=None)

        result = await resolve_hidden_subjects(db, user)

        assert result == {}
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_dict_returns_empty_dict(self):
        """Returns empty dict when hidden_subjects is empty dict."""
        db = AsyncMock()
        user = _make_user(hidden_subjects={})

        result = await resolve_hidden_subjects(db, user)

        assert result == {}
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolves_fully_hidden_subjects(self):
        """Resolves subject IDs to names with null types (fully hidden)."""
        db = AsyncMock()
        row1 = MagicMock()
        row1.id = 1
        row1.name = "Математика"
        row2 = MagicMock()
        row2.id = 2
        row2.name = "Физика"
        result_mock = MagicMock()
        result_mock.all.return_value = [row1, row2]
        db.execute.return_value = result_mock

        user = _make_user(hidden_subjects={"1": None, "2": None})

        with patch("src.utils.schedule_filters.select") as mock_select:
            mock_select.return_value.where.return_value = "query"
            result = await resolve_hidden_subjects(db, user)

        assert result == {"Математика": None, "Физика": None}
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_resolves_per_type_hidden_subjects(self):
        """Resolves subject IDs with specific lesson types."""
        db = AsyncMock()
        row1 = MagicMock()
        row1.id = 5
        row1.name = "Сети"
        result_mock = MagicMock()
        result_mock.all.return_value = [row1]
        db.execute.return_value = result_mock

        user = _make_user(hidden_subjects={"5": ["lab", "practice"]})

        with patch("src.utils.schedule_filters.select") as mock_select:
            mock_select.return_value.where.return_value = "query"
            result = await resolve_hidden_subjects(db, user)

        assert "Сети" in result
        assert result["Сети"] == {"lab", "practice"}

    @pytest.mark.asyncio
    async def test_skips_missing_subject_ids(self):
        """Skips subject IDs that don't exist in DB."""
        db = AsyncMock()
        row1 = MagicMock()
        row1.id = 1
        row1.name = "Математика"
        result_mock = MagicMock()
        result_mock.all.return_value = [row1]
        db.execute.return_value = result_mock

        user = _make_user(hidden_subjects={"1": None, "999": ["lab"]})

        with patch("src.utils.schedule_filters.select") as mock_select:
            mock_select.return_value.where.return_value = "query"
            result = await resolve_hidden_subjects(db, user)

        assert result == {"Математика": None}
