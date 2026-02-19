"""Tests for schedule entry filtering utilities."""

from unittest.mock import MagicMock

from src.utils.schedule_filters import filter_entries_by_user_prefs


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

    def test_no_hidden_subjects_passes_all(self):
        """All entries pass when hidden_subjects is None."""
        entries = [_make_entry(subject_id=1), _make_entry(subject_id=2)]
        user = _make_user(hidden_subjects=None)

        result = filter_entries_by_user_prefs(entries, user)

        assert len(result) == 2

    def test_empty_hidden_subjects_passes_all(self):
        """All entries pass when hidden_subjects is empty list."""
        entries = [_make_entry(subject_id=1), _make_entry(subject_id=2)]
        user = _make_user(hidden_subjects=[])

        result = filter_entries_by_user_prefs(entries, user)

        assert len(result) == 2

    def test_hidden_subject_is_filtered_out(self):
        """Entries with hidden subject_id are filtered out."""
        entries = [
            _make_entry(subject_id=1, subject_name="Математика"),
            _make_entry(subject_id=2, subject_name="Физика"),
            _make_entry(subject_id=3, subject_name="Химия"),
        ]
        user = _make_user(hidden_subjects=[2])

        result = filter_entries_by_user_prefs(entries, user)

        assert len(result) == 2
        assert all(e.subject_id != 2 for e in result)

    def test_entry_with_null_subject_id_not_filtered(self):
        """Entries with subject_id=None are never hidden."""
        entries = [
            _make_entry(subject_id=None, subject_name="Неизвестный"),
            _make_entry(subject_id=1, subject_name="Математика"),
        ]
        user = _make_user(hidden_subjects=[1])

        result = filter_entries_by_user_prefs(entries, user)

        assert len(result) == 1
        assert result[0].subject_id is None

    def test_multiple_hidden_subjects(self):
        """Multiple subjects can be hidden at once."""
        entries = [
            _make_entry(subject_id=1),
            _make_entry(subject_id=2),
            _make_entry(subject_id=3),
            _make_entry(subject_id=4),
        ]
        user = _make_user(hidden_subjects=[1, 3])

        result = filter_entries_by_user_prefs(entries, user)

        assert len(result) == 2
        ids = [e.subject_id for e in result]
        assert 1 not in ids
        assert 3 not in ids

    def test_hidden_subjects_combined_with_subgroup_filter(self):
        """Hidden subjects filter works alongside subgroup filter."""
        entries = [
            _make_entry(subject_id=1, subgroup=1),
            _make_entry(subject_id=1, subgroup=2),
            _make_entry(subject_id=2, subgroup=1),
        ]
        user = _make_user(preferred_subgroup=1, hidden_subjects=[2])

        result = filter_entries_by_user_prefs(entries, user)

        # subject_id=1 subgroup=2 filtered by subgroup
        # subject_id=2 subgroup=1 filtered by hidden
        assert len(result) == 1
        assert result[0].subject_id == 1
        assert result[0].subgroup == 1
