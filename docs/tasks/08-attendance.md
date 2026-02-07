# Задача: Посещаемость

## Приоритет: P2 (средний)
## Сложность: Средняя
## Затрагивает: Backend + Frontend

## Описание
Отметка посещаемости занятий: "был" / "пропустил" / "уважительная причина". Статистика по предметам и общая. Полезно перед сессией для оценки допуска.

## Зачем
Перед сессией преподаватели проверяют посещаемость. Студенту полезно знать заранее, хватает ли посещений для допуска.

---

## Чеклист

### Фаза 1: Backend — модель и миграция
- [ ] Создать модель `Attendance`:
  - `id`, `user_id`, `schedule_entry_id`, `status` (attended/missed/excused), `note`, `created_at`
  - UNIQUE constraint: (user_id, schedule_entry_id)
- [ ] Alembic миграция
- [ ] Создать `schemas/attendance.py` (AttendanceResponse, AttendanceUpdate, AttendanceStats)

### Фаза 2: Backend — сервис и API
- [ ] Создать `services/attendance.py`:
  - `mark_attendance(db, user_id, schedule_entry_id, status)` — отметить
  - `get_attendance(db, user_id, date_from, date_to)` — список
  - `get_stats(db, user_id, subject_name?)` — статистика
  - `get_today_attendance(db, user_id)` — посещаемость сегодня
- [ ] Создать `routers/attendance.py`:
  - `PUT /api/v1/attendance/{schedule_entry_id}` — отметить/обновить
  - `GET /api/v1/attendance?from=...&to=...` — список за период
  - `GET /api/v1/attendance/stats` — статистика (общая + по предметам)
  - `GET /api/v1/attendance/today` — сегодняшние пары с отметками

### Фаза 3: Frontend — интеграция в расписание
- [ ] В `LessonCard` добавить иконку посещаемости:
  - ✅ зелёная галочка — был
  - ❌ красный крестик — пропустил
  - ⚠️ жёлтый — уважительная причина
  - ⬜ серая — не отмечено (пара прошла)
  - Без иконки — пара ещё не была
- [ ] По клику на иконку — переключение статуса (attended → missed → excused → attended)
- [ ] Отмечать можно только прошедшие пары (не будущие)
- [ ] Создать `services/attendanceService.ts`

### Фаза 4: Frontend — страница статистики
- [ ] Создать `AttendanceStatsWidget.tsx` (для DashboardPage или SubjectsPage):
  - Общий прогресс: "Посетил 45 из 52 пар (87%)"
  - По предметам: таблица (предмет, посетил, пропустил, уваж., %)
  - Предупреждение если < 75% (красный)
- [ ] Добавить виджет на DashboardPage

### Фаза 5: Тесты
- [ ] Backend: тесты для attendance service (отметка, статистика, constraints)
- [ ] Backend: тесты для API endpoints
- [ ] Frontend: тесты для AttendanceStatsWidget

---

## Технические детали

### Модель БД
```python
class AttendanceStatus(str, Enum):
    ATTENDED = 'attended'
    MISSED = 'missed'
    EXCUSED = 'excused'

class Attendance(Base):
    __tablename__ = 'attendance'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    schedule_entry_id: Mapped[int] = mapped_column(ForeignKey('schedule_entries.id'))
    status: Mapped[AttendanceStatus]
    note: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'schedule_entry_id', name='uq_attendance'),
    )
```

### Статистика
```json
{
  "total_lessons": 52,
  "attended": 45,
  "missed": 5,
  "excused": 2,
  "unmarked": 0,
  "percentage": 86.5,
  "by_subject": [
    {
      "subject_name": "Математический анализ",
      "total": 16,
      "attended": 14,
      "missed": 2,
      "excused": 0,
      "percentage": 87.5,
      "warning": false
    }
  ]
}
```

### UX: быстрая отметка
```tsx
// Один клик — циклическое переключение статуса
const statusCycle = ['attended', 'missed', 'excused', null] as const
const handleToggle = () => {
  const currentIndex = statusCycle.indexOf(attendance?.status ?? null)
  const nextStatus = statusCycle[(currentIndex + 1) % statusCycle.length]
  if (nextStatus) {
    markAttendance.mutate({ scheduleEntryId, status: nextStatus })
  } else {
    deleteAttendance.mutate(scheduleEntryId)
  }
}
```

## Связанные файлы
- `backend/src/models/` — новая модель `attendance.py`
- `backend/src/services/` — новый `attendance.py`
- `backend/src/routers/` — новый `attendance.py`
- `frontend/src/components/schedule/LessonCard.tsx` — иконка посещаемости
- `frontend/src/pages/DashboardPage.tsx` — виджет статистики
