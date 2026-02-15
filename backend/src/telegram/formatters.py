"""Message formatters for Telegram bot."""

from __future__ import annotations

from datetime import time

from src.schemas.schedule import (
    CurrentLessonResponse,
    DayScheduleResponse,
    ScheduleEntryResponse,
    WeekScheduleResponse,
)

DAY_NAMES_RU = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}

LESSON_TYPE_EMOJI = {
    "lecture": "\U0001f4d6",
    "practice": "\u270f\ufe0f",
    "lab": "\U0001f9ea",
    "seminar": "\U0001f4ac",
    "exam": "\U0001f4dd",
    "consultation": "\U0001f4de",
    "other": "\U0001f4cc",
}


def _format_time(t: time) -> str:
    """Format time as HH:MM."""
    return t.strftime("%H:%M")


def _format_entry(entry: ScheduleEntryResponse) -> str:
    """Format a single schedule entry."""
    emoji = LESSON_TYPE_EMOJI.get(entry.lesson_type.value, "\U0001f4cc")
    parts = [f"{emoji} <b>{_format_time(entry.start_time)}-{_format_time(entry.end_time)}</b>"]
    parts.append(f"  {entry.subject_name}")
    if entry.teacher_name:
        parts.append(f"  \U0001f468\u200d\U0001f3eb {entry.teacher_name}")
    if entry.room or entry.building:
        location = ", ".join(filter(None, [entry.room, entry.building]))
        parts.append(f"  \U0001f4cd {location}")
    if entry.subgroup:
        parts.append(f"  \U0001f465 Подгруппа {entry.subgroup}")
    return "\n".join(parts)


def format_day_schedule(day: DayScheduleResponse) -> str:
    """Format a full day schedule."""
    day_name = DAY_NAMES_RU.get(day.day_of_week.value, day.day_name)
    header = f"\U0001f4c5 <b>{day_name}, {day.date.strftime('%d.%m')}</b>\n"

    if not day.entries:
        return header + "\n\U0001f389 Пар нет! Свободный день."

    entries = "\n\n".join(_format_entry(e) for e in day.entries)
    return header + "\n" + entries


def format_today_schedule(day: DayScheduleResponse) -> str:
    """Format today's schedule with a header."""
    return f"\U0001f4da <b>Расписание на сегодня</b>\n\n{format_day_schedule(day)}"


def format_tomorrow_schedule(day: DayScheduleResponse) -> str:
    """Format tomorrow's schedule with a header."""
    return f"\U0001f4da <b>Расписание на завтра</b>\n\n{format_day_schedule(day)}"


def format_week_schedule(week: WeekScheduleResponse) -> str:
    """Format a full week schedule."""
    week_type = "нечётная" if week.is_odd_week else "чётная"
    header = (
        f"\U0001f5d3 <b>Расписание на неделю</b> ({week_type})\n"
        f"{week.week_start.strftime('%d.%m')} — {week.week_end.strftime('%d.%m')}\n"
    )

    if not week.days:
        return header + "\n\U0001f389 На этой неделе пар нет!"

    days_text = "\n\n".join(format_day_schedule(d) for d in week.days)
    return header + "\n" + days_text


def format_current_lesson(data: CurrentLessonResponse) -> str:
    """Format current/next lesson info."""
    parts: list[str] = []

    if data.current:
        parts.append("\u2705 <b>Сейчас идёт:</b>")
        parts.append(_format_entry(data.current))

    if data.next:
        if data.current:
            parts.append("")
        parts.append("\u23ed <b>Следующее занятие:</b>")
        parts.append(_format_entry(data.next))
        if data.time_until_next is not None:
            hours, mins = divmod(data.time_until_next, 60)
            if hours > 0:
                parts.append(f"\n\u23f0 Через {hours}ч {mins}мин")
            else:
                parts.append(f"\n\u23f0 Через {mins} мин")

    if not parts:
        parts.append("\U0001f389 На сегодня пар больше нет!")

    return "\n".join(parts)


def format_deadlines(works: list) -> str:
    """Format upcoming deadlines."""
    if not works:
        return "\u2705 <b>Ближайших дедлайнов нет!</b>\nМожно расслабиться \U0001f60e"

    header = f"\u23f0 <b>Ближайшие дедлайны</b> ({len(works)} шт.)\n"
    items: list[str] = []
    for w in works:
        deadline_str = w.deadline.strftime("%d.%m %H:%M") if w.deadline else "—"
        subject_name = w.subject.name if w.subject else "—"
        items.append(
            f"\n\U0001f4cc <b>{w.title}</b>\n"
            f"  \U0001f4d6 {subject_name}\n"
            f"  \U0001f4c5 {deadline_str}"
        )
    return header + "\n".join(items)


def format_grades(grades: list) -> str:
    """Format session grades."""
    if not grades:
        return "\U0001f4da <b>Оценок пока нет.</b>"

    header = f"\U0001f393 <b>Оценки</b> ({len(grades)} шт.)\n"
    items: list[str] = []
    current_session = None
    for g in grades:
        if g.session_number != current_session:
            current_session = g.session_number
            items.append(f"\n\U0001f4cb <b>Сессия {g.session_number}</b>")
        items.append(f"  {g.subject_name}: <b>{g.result}</b>")
    return header + "\n".join(items)


def format_attendance(stats: dict) -> str:
    """Format attendance statistics."""
    total = stats.get("total_completed", 0)
    attended = stats.get("attended", 0)
    absences = stats.get("absences", 0)
    percent = stats.get("attendance_percent", 0)

    header = "\U0001f4ca <b>Посещаемость</b>\n"
    summary = (
        f"\n\u2705 Посещено: {attended}/{total}\n"
        f"\u274c Пропущено: {absences}\n"
        f"\U0001f4c8 Процент: {percent}%\n"
    )

    by_subject = stats.get("by_subject", [])
    if by_subject:
        summary += "\n<b>По предметам:</b>"
        for s in by_subject:
            summary += (
                f"\n  {s['subject_name']}: "
                f"{s['attended']}/{s['total_classes']} "
                f"({s['attendance_percent']}%)"
            )

    return header + summary


def format_schedule_changed() -> str:
    """Format schedule change notification."""
    return (
        "\U0001f514 <b>Расписание обновлено!</b>\n\n"
        "Были обнаружены изменения в расписании.\n"
        "Используйте /today или /week для просмотра актуального расписания."
    )


def format_morning_summary(
    day: DayScheduleResponse,
    upcoming_works: list,
) -> str:
    """Format the morning summary message."""
    parts = ["\u2600\ufe0f <b>Доброе утро!</b>\n"]
    parts.append(format_day_schedule(day))

    if upcoming_works:
        parts.append("\n\n\u23f0 <b>Ближайшие дедлайны:</b>")
        for w in upcoming_works[:3]:
            deadline_str = w.deadline.strftime("%d.%m %H:%M") if w.deadline else "—"
            parts.append(f"  \U0001f4cc {w.title} — {deadline_str}")

    return "\n".join(parts)


def format_deadline_alert(work: object) -> str:
    """Format a single deadline alert."""
    deadline_str = work.deadline.strftime("%d.%m %H:%M") if work.deadline else "—"  # type: ignore[union-attr]
    subject_name = work.subject.name if work.subject else "—"  # type: ignore[union-attr]
    return (
        f"\u26a0\ufe0f <b>Дедлайн скоро!</b>\n\n"
        f"\U0001f4cc <b>{work.title}</b>\n"  # type: ignore[union-attr]
        f"\U0001f4d6 {subject_name}\n"
        f"\U0001f4c5 {deadline_str}"
    )
