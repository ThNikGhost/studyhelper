"""Tests for schedule entry filtering utilities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.utils.schedule_filters import (
    filter_entries_by_user_prefs,
    resolve_hidden_subject_names,
)


def _make_entry(
    *,
    subject_id: int | None = None,
    subject_name: str = "Математика",
    teacher_name: str | None = None,
    subgroup: int | None = None,
) -> MagicMock:
    """Create a mock ScheduleEntry."""
    entry = MagicMock()
    entry.subject_id = subject_id
    entry.subject_name = subject_name
    entry.teacher_name = teacher_name
    entry.subgroup = subgroup
    return entry


def _make_user(
    *,
    preferred_subgroup: int | None = None,
    preferred_pe_teacher: str | None = None,
    hidden_subjects: list[int] | None = None,
) -> MagicMock:
    """Create a mock User."""
    user = MagicMock()
    user.preferred_subgroup = preferred_subgroup
    user.preferred_pe_teacher = preferred_pe_teacher
    user.hidden_subjects = hidden_subjects
    return user


class TestHiddenSubjectsFilter:
    """Tests for hidden subjects filtering in filter_entries_by_user_prefs."""

    def test_no_hidden_names_passes_all(self):
        """All entries pass when hidden_subject_names is None."""
        entries = [
            _make_entry(subject_name="Математика"),
            _make_entry(subject_name="Физика"),
        ]
        user = _make_user(hidden_subjects=None)

        result = filter_entries_by_user_prefs(entries, user, hidden_subject_names=None)

        assert len(result) == 2

    def test_empty_hidden_names_passes_all(self):
        """All entries pass when hidden_subject_names is empty set."""
        entries = [
            _make_entry(subject_name="Математика"),
            _make_entry(subject_name="Физика"),
        ]
        user = _make_user(hidden_subjects=[])

        result = filter_entries_by_user_prefs(entries, user, hidden_subject_names=set())

        assert len(result) == 2

    def test_hidden_subject_name_is_filtered_out(self):
        """Entries with hidden subject_name are filtered out."""
        entries = [
            _make_entry(subject_name="Математика"),
            _make_entry(subject_name="Физика"),
            _make_entry(subject_name="Химия"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subject_names={"Физика"}
        )

        assert len(result) == 2
        names = [e.subject_name for e in result]
        assert "Физика" not in names

    def test_entry_with_null_subject_name_not_filtered(self):
        """Entries with subject_name=None are never hidden."""
        entries = [
            _make_entry(subject_name=None),
            _make_entry(subject_name="Математика"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subject_names={"Математика"}
        )

        assert len(result) == 1
        assert result[0].subject_name is None

    def test_multiple_hidden_subject_names(self):
        """Multiple subjects can be hidden at once."""
        entries = [
            _make_entry(subject_name="Математика"),
            _make_entry(subject_name="Физика"),
            _make_entry(subject_name="Химия"),
            _make_entry(subject_name="Биология"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subject_names={"Математика", "Химия"}
        )

        assert len(result) == 2
        names = [e.subject_name for e in result]
        assert "Математика" not in names
        assert "Химия" not in names

    def test_hidden_subjects_combined_with_subgroup_filter(self):
        """Hidden subjects filter works alongside subgroup filter."""
        entries = [
            _make_entry(subject_name="Математика", subgroup=1),
            _make_entry(subject_name="Математика", subgroup=2),
            _make_entry(subject_name="Физика", subgroup=1),
        ]
        user = _make_user(preferred_subgroup=1)

        result = filter_entries_by_user_prefs(
            entries, user, hidden_subject_names={"Физика"}
        )

        # subject_name="Математика" subgroup=2 filtered by subgroup
        # subject_name="Физика" subgroup=1 filtered by hidden
        assert len(result) == 1
        assert result[0].subject_name == "Математика"
        assert result[0].subgroup == 1

    def test_no_hidden_names_param_passes_all(self):
        """All entries pass when hidden_subject_names param is not provided."""
        entries = [
            _make_entry(subject_name="Математика"),
            _make_entry(subject_name="Физика"),
        ]
        user = _make_user()

        result = filter_entries_by_user_prefs(entries, user)

        assert len(result) == 2


class TestResolveHiddenSubjectNames:
    """Tests for resolve_hidden_subject_names."""

    @pytest.mark.asyncio
    async def test_empty_hidden_subjects_returns_empty_set(self):
        """Returns empty set when user has no hidden subjects."""
        db = AsyncMock()
        user = _make_user(hidden_subjects=None)

        result = await resolve_hidden_subject_names(db, user)

        assert result == set()
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty_set(self):
        """Returns empty set when hidden_subjects is empty list."""
        db = AsyncMock()
        user = _make_user(hidden_subjects=[])

        result = await resolve_hidden_subject_names(db, user)

        assert result == set()
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolves_ids_to_names(self):
        """Resolves subject IDs to their names via DB query."""
        db = AsyncMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = ["Математика", "Физика"]
        result_mock = MagicMock()
        result_mock.scalars.return_value = scalars_mock
        db.execute.return_value = result_mock

        user = _make_user(hidden_subjects=[1, 2])

        with patch("src.utils.schedule_filters.select") as mock_select:
            mock_select.return_value.where.return_value = "query"
            result = await resolve_hidden_subject_names(db, user)

        assert result == {"Математика", "Физика"}
        db.execute.assert_called_once()
