"""SQLAlchemy models."""

from src.models.base import Base
from src.models.classmate import Classmate
from src.models.schedule import ScheduleEntry, ScheduleSnapshot
from src.models.semester import Semester
from src.models.subject import Subject
from src.models.teacher import Teacher
from src.models.university import Building, Department
from src.models.user import User
from src.models.work import Work, WorkStatus, WorkStatusHistory

__all__ = [
    "Base",
    "Building",
    "Classmate",
    "Department",
    "ScheduleEntry",
    "ScheduleSnapshot",
    "Semester",
    "Subject",
    "Teacher",
    "User",
    "Work",
    "WorkStatus",
    "WorkStatusHistory",
]
