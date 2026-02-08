# Текущая задача

## Статус
**08-attendance завершена** — реализована на ветке `main`, ожидает коммит.

## Выполнено: 08-attendance (посещаемость)

### Backend
- [x] `models/attendance.py` — модель Absence (id, user_id FK, schedule_entry_id FK, created_at, UniqueConstraint)
- [x] `models/__init__.py` — Absence в импорты
- [x] `schemas/attendance.py` — AbsenceCreate, AbsenceResponse, MarkPresentRequest, AttendanceEntryResponse, SubjectAttendanceStats, AttendanceStatsResponse
- [x] `services/attendance.py` — mark_absent, mark_present, get_attendance_entries (filters), get_attendance_stats, get_subject_attendance_stats
- [x] `routers/attendance.py` — POST /mark-absent (201), POST /mark-present (204), GET / (entries), GET /stats, GET /stats/{subject_id}
- [x] `main.py` — attendance router (prefix="/attendance", tags=["Attendance"])
- [x] Alembic миграция add_absences_table (df769e398a43)
- [x] 22 backend тестов (mark_absent: 7, mark_present: 3, get_attendance: 5, get_stats: 5, subject_stats: 2)

### Frontend
- [x] `types/attendance.ts` — AttendanceEntry, AbsenceRecord, SubjectAttendanceStats, AttendanceStats
- [x] `services/attendanceService.ts` — getEntries, markAbsent, markPresent, getStats, getSubjectStats
- [x] `lib/attendanceUtils.ts` — formatAttendancePercent, getAttendanceColor, getAttendanceBarColor, lessonTypeLabels
- [x] `components/attendance/AttendanceStatsCard.tsx` — карточка статистики с ProgressBar и процентом
- [x] `components/attendance/SubjectAttendanceList.tsx` — список предметов с мини-прогресс-барами, фильтр
- [x] `components/attendance/AttendanceTable.tsx` — таблица занятий с toggle кнопками Был/Н/Б
- [x] `pages/AttendancePage.tsx` — полная страница: stats, subject filter, entries table, mutations + toast
- [x] `App.tsx` — маршрут /attendance (ProtectedRoute + AppLayout)
- [x] `QuickActions.tsx` — пункт "Посещаемость" (CheckCircle2, text-teal-500)
- [x] MSW handlers: GET /attendance/, GET /attendance/stats, POST mark-absent, POST mark-present
- [x] 32 frontend тестов (attendanceUtils: 12, AttendanceStatsCard: 5, AttendanceTable: 7, AttendancePage: 8)
- [x] TypeScript, ESLint, build — всё чисто

## Следующие задачи (приоритет)
1. **09-dark-theme** — тёмная тема (P2)
2. **05-ics-export** — экспорт в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1, зависит от PWA)
4. **10-lesson-notes** — заметки к парам (P2)
5. **11-semester-timeline** — timeline семестра (P3)

## Заметки
- Backend: 307 тестов проходят (285 + 22 новых)
- Frontend: 258 тестов проходят (226 + 32 новых)
- Все линтеры чисты
- Архитектура: absences-only (хранятся только пропуски)
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
