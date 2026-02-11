"""SQLAlchemy models."""

from src.models.attendance import Absence
from src.models.base import Base
from src.models.classmate import Classmate
from src.models.file import File
from src.models.lk import LkCredentials, SemesterDiscipline, SessionGrade
from src.models.note import LessonNote
from src.models.schedule import ScheduleEntry, ScheduleSnapshot
from src.models.semester import Semester
from src.models.subject import Subject
from src.models.teacher import Teacher
from src.models.university import Building, Department
from src.models.user import User
from src.models.work import Work, WorkStatus, WorkStatusHistory

__all__ = [
    "Absence",
    "Base",
    "Building",
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
    "User",
    "Work",
    "WorkStatus",
    "WorkStatusHistory",
]
