"""Tests for Telegram message formatters."""

from datetime import date, time

from src.schemas.schedule import (
    CurrentLessonResponse,
    DayOfWeek,
    DayScheduleResponse,
    LessonType,
    ScheduleEntryResponse,
    WeekScheduleResponse,
)
from src.telegram.formatters import (
    format_attendance,
    format_current_lesson,
    format_day_schedule,
    format_deadlines,
    format_grades,
    format_today_schedule,
    format_week_schedule,
)


def _make_entry(**kwargs) -> ScheduleEntryResponse:
    """Create a schedule entry for testing."""
    from datetime import datetime

    defaults = {
        "id": 1,
        "lesson_date": date(2026, 2, 16),
        "day_of_week": DayOfWeek.MONDAY,
        "start_time": time(8, 0),
        "end_time": time(9, 35),
        "subject_name": "Математика",
        "lesson_type": LessonType.LECTURE,
        "teacher_name": "Иванов И.И.",
        "room": "301",
        "building": "1 корпус",
        "group_name": None,
        "subgroup": None,
        "notes": None,
        "subject_id": None,
        "teacher_id": None,
        "week_type": None,
        "created_at": datetime(2026, 1, 1),
        "updated_at": datetime(2026, 1, 1),
    }
    defaults.update(kwargs)
    return ScheduleEntryResponse(**defaults)


class TestFormatDaySchedule:
    """Tests for format_day_schedule."""

    def test_empty_day(self) -> None:
        """Should show 'no lessons' for empty day."""
        day = DayScheduleResponse(
            date=date(2026, 2, 16),
            day_of_week=DayOfWeek.MONDAY,
            day_name="Понедельник",
            entries=[],
        )
        result = format_day_schedule(day)
        assert "Пар нет" in result
        assert "Понедельник" in result

    def test_day_with_entries(self) -> None:
        """Should format entries with times and details."""
        day = DayScheduleResponse(
            date=date(2026, 2, 16),
            day_of_week=DayOfWeek.MONDAY,
            day_name="Понедельник",
            entries=[_make_entry()],
        )
        result = format_day_schedule(day)
        assert "08:00-09:35" in result
        assert "Математика" in result
        assert "Иванов И.И." in result
        assert "301" in result

    def test_subgroup_shown(self) -> None:
        """Should show subgroup when present."""
        day = DayScheduleResponse(
            date=date(2026, 2, 16),
            day_of_week=DayOfWeek.MONDAY,
            day_name="Понедельник",
            entries=[_make_entry(subgroup=2)],
        )
        result = format_day_schedule(day)
        assert "Подгруппа 2" in result


class TestFormatTodaySchedule:
    """Tests for format_today_schedule."""

    def test_has_header(self) -> None:
        """Should include 'today' header."""
        day = DayScheduleResponse(
            date=date(2026, 2, 16),
            day_of_week=DayOfWeek.MONDAY,
            day_name="Понедельник",
            entries=[],
        )
        result = format_today_schedule(day)
        assert "сегодня" in result.lower()


class TestFormatWeekSchedule:
    """Tests for format_week_schedule."""

    def test_empty_week(self) -> None:
        """Should show 'no lessons' for empty week."""
        week = WeekScheduleResponse(
            week_start=date(2026, 2, 16),
            week_end=date(2026, 2, 22),
            week_number=8,
            is_odd_week=True,
            days=[],
        )
        result = format_week_schedule(week)
        assert "пар нет" in result.lower()

    def test_shows_week_type(self) -> None:
        """Should show odd/even week type."""
        week = WeekScheduleResponse(
            week_start=date(2026, 2, 16),
            week_end=date(2026, 2, 22),
            week_number=8,
            is_odd_week=True,
            days=[],
        )
        result = format_week_schedule(week)
        assert "нечётная" in result


class TestFormatCurrentLesson:
    """Tests for format_current_lesson."""

    def test_no_lessons(self) -> None:
        """Should show 'no more lessons' when both current and next are None."""
        data = CurrentLessonResponse(current=None, next=None, time_until_next=None)
        result = format_current_lesson(data)
        assert "больше нет" in result.lower()

    def test_current_lesson(self) -> None:
        """Should show current lesson."""
        data = CurrentLessonResponse(
            current=_make_entry(),
            next=None,
            time_until_next=None,
        )
        result = format_current_lesson(data)
        assert "Сейчас" in result
        assert "Математика" in result

    def test_next_lesson_with_time(self) -> None:
        """Should show time until next lesson."""
        data = CurrentLessonResponse(
            current=None,
            next=_make_entry(start_time=time(10, 0)),
            time_until_next=45,
        )
        result = format_current_lesson(data)
        assert "Следующее" in result
        assert "45 мин" in result


class TestFormatDeadlines:
    """Tests for format_deadlines."""

    def test_no_deadlines(self) -> None:
        """Should show 'no deadlines' message."""
        result = format_deadlines([])
        assert "нет" in result.lower()


class TestFormatGrades:
    """Tests for format_grades."""

    def test_no_grades(self) -> None:
        """Should show 'no grades' message."""
        result = format_grades([])
        assert "нет" in result.lower()


class TestFormatAttendance:
    """Tests for format_attendance."""

    def test_basic_stats(self) -> None:
        """Should show attendance percentage."""
        stats = {
            "total_completed": 30,
            "attended": 27,
            "absences": 3,
            "attendance_percent": 90.0,
            "by_subject": [],
        }
        result = format_attendance(stats)
        assert "90.0%" in result
        assert "27" in result
        assert "3" in result
