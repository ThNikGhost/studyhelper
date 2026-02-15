"""SQLAlchemy models."""

from src.models.attendance import Absence
from src.models.base import Base
from src.models.calendar_feed import CalendarFeed
from src.models.classmate import Classmate
from src.models.file import File
from src.models.lk import LkCredentials, SemesterDiscipline, SessionGrade
from src.models.note import LessonNote
from src.models.schedule import ScheduleEntry, ScheduleSnapshot
from src.models.semester import Semester
from src.models.subject import Subject
from src.models.teacher import Teacher
from src.models.telegram import TelegramLink
from src.models.university import Building, Department
from src.models.user import User
from src.models.widget_api_key import WidgetApiKey
from src.models.work import Work, WorkStatus, WorkStatusHistory

__all__ = [
    "Absence",
    "Base",
    "Building",
    "CalendarFeed",
    "Classmate",
    "Department",
    "File",
    "LessonNote",
    "LkCredentials",
    "ScheduleEntry",
    "ScheduleSnapshot",
    "Semester",
    "SemesterDiscipline",
    "SessionGrade",
    "Subject",
    "Teacher",
    "TelegramLink",
    "User",
    "WidgetApiKey",
    "Work",
    "WorkStatus",
    "WorkStatusHistory",
]
