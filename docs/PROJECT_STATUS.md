# Статус проекта StudyHelper

## Последнее обновление
- **Дата**: 2026-02-12
- **Сессия**: LK Integration — Frontend (зачётка, настройки ЛК, импорт)

## Общий прогресс
**Фаза**: Production
**Прогресс**: MVP 100% завершён. Все post-MVP фичи реализованы. Production задеплоен с SSL на https://studyhelper1.ru. Certbot auto-renewal настроен.

---

## Что сделано

### Документация
- [x] Техническое задание (docs/StudyHelper_TZ.md)
- [x] CLAUDE.md — обновлён под проект
- [x] plans/MVP_plan.md — план MVP
- [x] plans/backend_plan.md — план backend разработки
- [x] plans/future_features.md — планы на будущее
- [x] plans/schedule_page_frontend_plan.md — план SchedulePage
- [x] plans/enchanted-humming-lynx.md — план Code Review (8 фаз)

### Инфраструктура
- [x] Docker Compose (PostgreSQL 16, Redis 7, Adminer) — для Linux/Mac
- [x] Локальный PostgreSQL — для Windows
- [x] .env.example — переменные окружения (backend + frontend)
- [x] GitHub repository
- [x] GitHub Actions CI (backend lint+test + frontend lint+build) — fixed

### Backend (ЗАВЕРШЁН)
- [x] Инициализация проекта (pyproject.toml, uv)
- [x] Конфигурация (pydantic-settings)
- [x] База данных (SQLAlchemy 2.0 async)
- [x] Alembic миграции (18 миграций применено)

#### Модули:
| Модуль | Модель | Схемы | Сервис | Роутер | Тесты |
|--------|--------|-------|--------|--------|-------|
| Auth | ✅ User | ✅ | ✅ | ✅ | ✅ 16 |
| Semesters | ✅ (+start_date, end_date) | ✅ (+Timeline) | ✅ (+timeline) | ✅ (+timeline) | ✅ 26 |
| Subjects | ✅ (+planned_classes, +total_hours) | ✅ | ✅ | ✅ | ✅ 18 |
| Works | ✅ Work, WorkStatus, WorkStatusHistory | ✅ | ✅ | ✅ | ✅ 23 |
| Teachers | ✅ | ✅ | ✅ | ✅ | ✅ 20 |
| University | ✅ Department, Building | ✅ | ✅ | ✅ | ✅ 28 |
| Classmates | ✅ | ✅ | ✅ | ✅ | ✅ 20 |
| Schedule | ✅ ScheduleEntry, ScheduleSnapshot | ✅ | ✅ | ✅ | ✅ 24+11 |
| Parser | ✅ (+subgroup parsing) | ✅ | ✅ | CLI | ✅ 82 |
| Uploads | — | ✅ | ✅ | ✅ | ✅ 11 |
| Files | ✅ File | ✅ | ✅ | ✅ | ✅ 21 |
| Attendance | ✅ Absence | ✅ (+total_planned/completed) | ✅ (semester filter) | ✅ | ✅ 29 |
| Notes | ✅ LessonNote | ✅ | ✅ | ✅ | ✅ 26 |
| LK | ✅ LkCredentials, SessionGrade, SemesterDiscipline | ✅ (+LkImportResult) | ✅ (+import_to_app) | ✅ (+/import) | ✅ 51 |

### Parser модуль (ЗАВЕРШЁН ✅)
- [x] `src/parser/` — модуль парсинга
- [x] `src/cli/schedule_cli.py` — CLI команды (parse, sync)
- [x] `src/tasks/schedule_tasks.py` — Celery задачи (подготовлены)
- [x] `POST /api/v1/schedule/refresh` — API endpoint для синхронизации
- [x] Протестировано на реальном API: **3088 записей**

### Frontend (ЗАВЕРШЁН ✅)
- [x] Инициализация Vite + React 19 + TypeScript
- [x] Tailwind CSS v4 настроен
- [x] UI компоненты (Button, Input, Card, Label, Calendar, Popover, Modal)
- [x] API клиент (axios с interceptors для JWT + token refresh mutex)
- [x] Auth store (Zustand)
- [x] Роутинг (react-router-dom)
- [x] Защищённые маршруты (ProtectedRoute)
- [x] ErrorBoundary компонент
- [x] Страницы: LoginPage, RegisterPage, DashboardPage
- [x] SchedulePage ✅ (кастомный календарь, локальное время)
- [x] SubjectsPage ✅ (+total_hours display)
- [x] WorksPage ✅
- [x] SemestersPage ✅ (CRUD для семестров, +Import from LK)
- [x] ClassmatesPage ✅ (CRUD, контакты, санитизация Telegram)
- [x] GradesPage ✅ (NEW: зачётка с оценками по сессиям)
- [x] SettingsPage ✅ (подгруппа, физра, ЛК credentials)

### Frontend тесты (ЗАВЕРШЁН ✅)
- [x] Тестовая инфраструктура: Vitest + @testing-library/react + MSW
- [x] Тесты утилит: dateUtils (31), errorUtils (13), constants (6)
- [x] Тесты store: authStore (11)
- [x] Тесты компонентов: ProtectedRoute (3), ErrorBoundary (3), Modal (6)
- [x] Тесты страниц: LoginPage (6), DashboardPage (10)
- [x] Тесты dashboard виджетов: TodayScheduleWidget (10), DeadlinesWidget (10)
- [x] TypeScript + ESLint чисто на тестовых файлах

### Code Review (ЗАВЕРШЁН ✅)
- [x] Фаза 0: GitHub Actions CI
- [x] Фаза 1: Backend Security (secret_key validation, CORS, rate limiting, security headers, exception handler)
- [x] Фаза 2: Upload Security (streaming reads, magic bytes, path traversal, UploadService)
- [x] Фаза 3: Backend Code Quality (specific exceptions, atomic updates, rollback, logging, ZoneInfo, TypedDict)
- [x] Фаза 4: Frontend Infrastructure (ErrorBoundary, token refresh mutex, AbortController, toast, Modal, dateUtils, errorUtils, constants)
- [x] Фаза 5: Frontend Page Fixes (shared Modal/toast/spinners on all pages, timezone fix, Telegram sanitization, logout confirm)
- [x] Фаза 6: Backend Minor & Nitpick (max_length in schemas, HttpUrl helper, DB index, docstrings in exceptions)
- [x] Фаза 7: Frontend Minor & Nitpick (ESLint rules, DayOfWeek JSDoc)

### 01-PWA (ЗАВЕРШЕНА ✅) — merged в `main`
- [x] `vite-plugin-pwa` + `VitePWA()` конфигурация (generateSW, registerType: prompt)
- [x] Web manifest (name, icons, theme_color, lang: ru, display: standalone)
- [x] Мета-теги в index.html (theme-color, apple-mobile-web-app, description)
- [x] Иконки: pwa-192x192.png, pwa-512x512.png, apple-touch-icon-180x180.png, favicon.svg
- [x] Workbox: precache app shell + NetworkFirst для `/api/v1/*` (timeout 3s)
- [x] Offline fallback: `public/offline.html`
- [x] `useNetworkStatus` хук (online/offline + isMounted guard)
- [x] `NetworkStatusBar` — amber баннер при офлайне (role="alert")
- [x] `UpdatePrompt` — баннер обновления SW с shadcn/ui Button
- [x] `AppLayout` — обёртка для protected routes
- [x] 5 страниц: кнопки disabled в офлайне (Works, Subjects, Semesters, Classmates, Schedule)
- [x] 17 новых тестов (pwa-mock.ts, useNetworkStatus, NetworkStatusBar, UpdatePrompt, AppLayout)
- [x] Code review + исправление всех замечаний (P0/P1/P2)

### 04-dashboard-widget (ЗАВЕРШЕНА ✅)
- [x] `TodayScheduleWidget` — все пары на сегодня, текущая подсвечена, прошедшие приглушены, badge "через X мин"
- [x] `DeadlinesWidget` — группировка по срочности (Просрочено/Сегодня-Завтра/На неделе), badge просроченных, до 8 элементов
- [x] `QuickActions` — вынесен в отдельный компонент, адаптивная сетка `grid-cols-2 sm:grid-cols-3 lg:grid-cols-5`
- [x] `formatTime()`, `formatTimeUntil()` — утилиты перенесены в dateUtils
- [x] Рефакторинг DashboardPage — замена inline-виджетов на импорты, добавлен query `/schedule/today`
- [x] MSW handlers обновлены (mock `/schedule/today`, test data)
- [x] 27 новых тестов (TodayScheduleWidget: 10, DeadlinesWidget: 10, dateUtils: 7)
- [x] TypeScript, ESLint, build — всё чисто

### 06-clickable-schedule (ЗАВЕРШЕНА ✅)
- [x] `LessonDetailModal` — модал с полной информацией о занятии, работами по предмету, редактируемыми заметками
- [x] `LessonCard`, `ScheduleGrid`, `DayScheduleCard`, `TodayScheduleWidget` — onClick/onEntryClick props, hover, keyboard a11y
- [x] `SchedulePage`, `DashboardPage` — интеграция selectedEntry state + LessonDetailModal
- [x] `ScheduleEntryUpdate` тип + `updateEntry()` метод в scheduleService
- [x] MSW handlers: PUT schedule entry, GET works с фильтром subject_id
- [x] `tsconfig.app.json` — exclude тестовых файлов из build (fix pre-existing issue)
- [x] 31 новый тест (LessonDetailModal: 19, LessonCard: 12)
- [x] TypeScript, ESLint, build — всё чисто

### 07-progress-bars (ЗАВЕРШЕНА ✅)
- [x] `lib/progressUtils.ts` — типы SubjectProgress/SemesterProgress, calculateSemesterProgress, getProgressColor, getProgressBarColor
- [x] `components/ui/progress-bar.tsx` — ProgressBar (value, color, size, showLabel, aria)
- [x] `components/subjects/SubjectProgressCard.tsx` — карточка предмета с прогресс-баром, статистикой, status badges
- [x] `components/dashboard/SemesterProgressWidget.tsx` — виджет общего прогресса, топ-3 предмета с наименьшим прогрессом
- [x] SubjectsPage — общий прогресс вверху, SubjectProgressCard, навигация на WorksPage
- [x] DashboardPage — SemesterProgressWidget в grid виджетов
- [x] MSW handlers: GET /api/v1/subjects, расширенные тестовые данные работ
- [x] 38 новых тестов (progressUtils: 15, ProgressBar: 8, SubjectProgressCard: 7, SemesterProgressWidget: 8)
- [x] TypeScript, ESLint, build — всё чисто

### 03-file-upload-ui (ЗАВЕРШЕНА ✅)
- [x] Backend: модель File, схемы (FileCategory, FileResponse), сервис (upload/list/download/delete), роутер, миграция
- [x] Backend: validate_file_content (magic bytes), параметризованный read_upload_streaming, path traversal protection
- [x] Backend: config (max_file_size_mb=50, allowed_file_extensions, allowed_file_mime_types)
- [x] Backend: 21 тест (upload: 10, list: 5, download: 3, delete: 3)
- [x] Frontend: типы (FileCategory, StudyFile), сервис (fileService), утилиты (fileUtils)
- [x] Frontend: FileDropzone (HTML5 drag & drop, валидация, category/subject selects, progress bar)
- [x] Frontend: FileList (иконки по типу, metadata, download/delete)
- [x] Frontend: FilesPage (dropzone, фильтры, список, модал удаления, TanStack Query)
- [x] Frontend: маршрут /files в App.tsx, пункт "Файлы" в QuickActions
- [x] Frontend: 43 теста (fileUtils: 20, FileDropzone: 8, FileList: 7, FilesPage: 8)
- [x] TypeScript, ESLint, build — всё чисто

### 08-attendance (ЗАВЕРШЕНА ✅)
- [x] Backend: модель Absence (absences-only), UniqueConstraint(user_id, schedule_entry_id), indexes
- [x] Backend: схемы (AbsenceCreate, AbsenceResponse, AttendanceEntryResponse, SubjectAttendanceStats, AttendanceStatsResponse)
- [x] Backend: сервис (mark_absent, mark_present, get_attendance_entries, get_attendance_stats, get_subject_attendance_stats)
- [x] Backend: роутер (POST mark-absent 201, POST mark-present 204, GET entries, GET stats, GET stats/{subject_id})
- [x] Backend: Alembic миграция add_absences_table
- [x] Backend: 22 теста (mark_absent: 7, mark_present: 3, entries: 5, stats: 5, subject_stats: 2)
- [x] Frontend: типы (AttendanceEntry, AbsenceRecord, AttendanceStats, SubjectAttendanceStats)
- [x] Frontend: сервис (attendanceService: getEntries, markAbsent, markPresent, getStats, getSubjectStats)
- [x] Frontend: утилиты (formatAttendancePercent, getAttendanceColor, getAttendanceBarColor, lessonTypeLabels)
- [x] Frontend: AttendanceStatsCard (ProgressBar + общая статистика)
- [x] Frontend: SubjectAttendanceList (per-subject mini progress bars, clickable filter)
- [x] Frontend: AttendanceTable (entries list with toggle buttons Был/Н/Б)
- [x] Frontend: AttendancePage (stats card, subject filter, entries table, TanStack Query + mutations)
- [x] Frontend: маршрут /attendance в App.tsx, пункт "Посещаемость" (CheckCircle2, text-teal-500) в QuickActions
- [x] Frontend: MSW handlers + testAttendanceEntries + testAttendanceStats
- [x] Frontend: 32 теста (attendanceUtils: 12, AttendanceStatsCard: 5, AttendanceTable: 7, AttendancePage: 8)
- [x] TypeScript, ESLint, build — всё чисто

### 10-lesson-notes (ЗАВЕРШЕНА ✅)
- [x] Backend: модель LessonNote (user_id FK, schedule_entry_id FK nullable, subject_name, lesson_date, content Text)
- [x] Backend: UniqueConstraint(user_id, subject_name), indexes (user_id+lesson_date)
- [x] Backend: схемы (LessonNoteCreate, LessonNoteUpdate, LessonNoteResponse)
- [x] Backend: сервис (create_note upsert, update_note, delete_note, get_notes с фильтрами, get_note_for_entry, get_note_for_subject)
- [x] Backend: роутер (POST / 201|200 upsert, GET /, GET /subject/{name}, GET /entry/{id}, PUT /{id}, DELETE /{id} 204)
- [x] Backend: Alembic миграции: add_lesson_notes_table + change_note_unique_to_subject (14 миграций)
- [x] Backend: 26 тестов (create: 7, upsert: 2, get_notes: 5, get_note_for_entry: 3, get_note_for_subject: 4, update: 4, delete: 3)
- [x] Frontend: типы (LessonNote, LessonNoteCreate, LessonNoteUpdate)
- [x] Frontend: сервис (noteService: getNotes, getNoteForEntry, getNoteForSubject, createNote, updateNote, deleteNote)
- [x] Frontend: NoteEditor (autosave debounce 500ms, status indicator, char counter 2000, disabled)
- [x] Frontend: NoteCard (subject/date, content preview 150 chars, expand/collapse, delete)
- [x] Frontend: NotesPage (search debounce 300ms, subject filter, NoteCard list, delete confirm modal)
- [x] Frontend: LessonDetailModal — query по subject_name, cache invalidation через onSaved callback
- [x] Frontend: LessonCard — иконка StickyNote (amber-500) при наличии заметки (hasNote prop)
- [x] Frontend: ScheduleGrid, DayScheduleCard, SchedulePage — noteSubjectNames Set из API
- [x] Frontend: маршрут /notes в App.tsx, пункт "Заметки" (StickyNote, text-yellow-500) в QuickActions
- [x] Frontend: MSW handlers (+ GET /notes/subject/:subjectName) + testLessonNotes data
- [x] Frontend: 23 новых теста (NoteEditor: 10, NoteCard: 5, NotesPage: 8) + обновлены LessonDetailModal тесты (17)
- [x] TypeScript, ESLint, build — всё чисто

### 11-semester-timeline (ЗАВЕРШЕНА ✅)
- [x] Backend: start_date/end_date в модели Semester (Date, nullable), Alembic миграция
- [x] Backend: model_validator на SemesterCreate/SemesterUpdate (start_date < end_date)
- [x] Backend: TimelineDeadline, TimelineExam, TimelineResponse схемы
- [x] Backend: get_semester_timeline() сервис (works с deadline + user status, exams в диапазоне дат)
- [x] Backend: GET /api/v1/semesters/{id}/timeline endpoint (400 no dates, 404 not found)
- [x] Backend: 9 новых тестов (create/update with dates, invalid dates, timeline success/deadlines/no_dates/not_found/unauthorized/empty)
- [x] Frontend: типы TimelineDeadline, TimelineExam, TimelineData
- [x] Frontend: getSemesterTimeline() в subjectService
- [x] Frontend: timelineUtils (getPositionPercent, getMonthLabels, getSemesterProgress, getMarkerColor, getExamMarkerColor)
- [x] Frontend: TimelineBar (горизонтальная полоса, маркеры дедлайнов/экзаменов, "Сегодня", ось месяцев)
- [x] Frontend: TimelineMarker (Popover tooltip, circle/diamond variants)
- [x] Frontend: TimelineLegend, TimelineEventList
- [x] Frontend: TimelinePage (фильтры showDeadlines/showExams, subject dropdown, loading/error/empty states)
- [x] Frontend: SemesterTimelineWidget (dashboard widget, simplified bar)
- [x] Frontend: SemestersPage — date pickers в форме создания/редактирования
- [x] Frontend: DashboardPage — SemesterTimelineWidget в grid
- [x] Frontend: маршрут /timeline, пункт "Timeline" (BarChart3, text-indigo-500) в QuickActions
- [x] Frontend: MSW handlers + testSemester/testTimelineData
- [x] Frontend: 42 новых теста (timelineUtils: 21, TimelineBar: 8, SemesterTimelineWidget: 5, TimelinePage: 8)
- [x] TypeScript, ESLint, build — всё чисто

### 09-dark-theme (ЗАВЕРШЕНА ✅)
- [x] Frontend: `lib/theme.ts` — ThemeMode, getSavedTheme, saveTheme, resolveTheme, applyTheme
- [x] Frontend: `hooks/useTheme.ts` — React hook (mode, resolvedTheme, setTheme), system preference listener
- [x] Frontend: `index.html` — inline FOUC prevention script, dark fallback styles
- [x] Frontend: `components/ThemeToggle.tsx` — cycling button (Sun → Moon → Monitor), aria-label
- [x] Frontend: `components/AppLayout.tsx` — ThemeToggle в fixed bottom-right z-50
- [x] Frontend: `main.tsx` — theme="system" на Toaster (sonner)
- [x] Frontend: `lib/attendanceUtils.ts` — text-*-600 → + dark:text-*-400
- [x] Frontend: `components/attendance/AttendanceStatsCard.tsx` — + dark:text-red-400
- [x] Frontend: `components/attendance/AttendanceTable.tsx` — + dark:bg-red-950/30
- [x] Frontend: `public/offline.html` — @media (prefers-color-scheme: dark)
- [x] Frontend: 30 новых тестов (theme: 14, useTheme: 6, ThemeToggle: 6, AppLayout: +1, attendanceUtils: updated 3)
- [x] TypeScript, ESLint, build — всё чисто

---

### 12-schedule-auto-sync (ЗАВЕРШЕНА ✅)
- [x] Backend: `src/scheduler.py` — APScheduler `AsyncIOScheduler` + Redis distributed lock
- [x] Backend: `_sync_schedule_with_lock()` — non-blocking Redis lock (TTL 600s), calls `sync_schedule(db)`
- [x] Backend: `start_scheduler()` / `stop_scheduler()` — lifecycle в lifespan FastAPI
- [x] Backend: config: `schedule_sync_enabled`, `schedule_sync_lock_ttl_seconds`
- [x] Backend: зависимости: `apscheduler>=3.10.0,<4.0`, `redis>=5.0.0`
- [x] Backend: 11 тестов (lock acquire+run, lock skip, lock release on error, lock expired, redis reconnect, disabled, enabled, stop, stop noop)
- [x] `entrypoint.sh` — первичная синхронизация при запуске (если snapshot нет), non-blocking
- [x] `docker-compose.prod.yml` — env vars: `SCHEDULE_SYNC_ENABLED`, `SCHEDULE_UPDATE_INTERVAL_HOURS`
- [x] Code review fixes: jitter=60, misfire_grace_time=3600, Redis reconnect, LockNotOwnedError
- [x] `.gitattributes` — `*.sh text eol=lf` для Docker совместимости
- [x] Ruff check + format — чисто
- [x] 348 тестов backend — все проходят

### CI Fix (ЗАВЕРШЕНА ✅)
- [x] `frontend/eslint.config.js` — globalIgnores для `src/components/ui` (shadcn/ui)
- [x] `.github/workflows/ci.yml` — `uv sync --extra dev` вместо `uv sync --dev`
- [x] `backend/src/services/upload.py` — кросс-платформенная path traversal защита (бэкслэш + `..`)

### Production Docker (ЗАВЕРШЕНА ✅)
- [x] `backend/Dockerfile` — multi-stage build (python:3.12-slim + uv), non-root user (UID 1000), healthcheck
- [x] `backend/Dockerfile` — исправлено: добавлено `COPY README.md` для uv sync (коммит a6a6448)
- [x] `backend/entrypoint.sh` — wait for PostgreSQL, alembic migrate, uvicorn с --proxy-headers
- [x] `backend/.dockerignore` — исключает .venv, tests, uploads, __pycache__
- [x] `nginx/nginx.conf` — reverse proxy, rate limiting (30r/s API, 5r/m auth), gzip, security headers, PWA caching
- [x] `nginx/Dockerfile` — multi-stage (node:22 build → nginx:1.27-alpine serve)
- [x] `docker-compose.prod.yml` — 4 сервиса: db (512MB), redis (192MB), backend (512MB), nginx (128MB)
- [x] `.env.production.example` — шаблон env для продакшена
- [x] `.dockerignore` (корень) — для nginx build context
- [x] `.gitignore` — добавлено `!.env.production.example`

### Production Deployment (ЗАВЕРШЕНА ✅) — 2026-02-09
- [x] Phase 1: Регенерация секретов (SECRET_KEY 64 символа, POSTGRES_PASSWORD 32 символа)
- [x] Phase 2: Сборка Docker образов (backend + nginx, исправлен README.md issue)
- [x] Phase 3: Запуск контейнеров (исправлен ALLOWED_ORIGINS в JSON формат)
- [x] Phase 4: Применение миграций (все 13 миграций успешно)
- [x] Phase 5: Проверка работоспособности (health check ✅, frontend ✅, первый пользователь создан)
- [x] Деплой на сервер 89.110.93.63 — **приложение работает и доступно**

### Post-Deployment Verification (2026-02-09)
- [x] Настроено тестовое окружение на сервере (`uv` установлен, зависимости синхронизированы)
- [x] Запущены тесты backend на сервере — 18/18 passed (auth + health модули)
- [x] Диагностика расписания — 3088 записей в БД, API работает корректно
- [x] Проверено отображение расписания — frontend успешно загружает и показывает данные

### Bugfixes + DX (2026-02-11)
- [x] Fix: Modal `useEffect` — фокус крался при ре-рендере. Исправлено: `onCloseRef` + зависимость только `[open]`
- [x] Feat: PE teacher filter — `isPeEntry`, `filterPeEntries`, `filterDaySchedule`, `filterWeekSchedule`, localStorage, `PeTeacherSelect`
- [x] Fix: `formatTimeUntil` принимал секунды, backend отдаёт минуты — обновлены тесты, моки, SchedulePage
- [x] Fix: SchedulePage вручную делил `time_until_next / 60` — заменено на `formatTimeUntil()`
- [x] DX: `.claude/agents/test-runner.md` — агент для запуска тестов (Vitest на Windows зависает, агент запускает в фоне, парсит вывод, убивает процесс)
- [x] Деплой на сервер — nginx пересобран, все контейнеры здоровы

### Notes per-subject refactor (2026-02-11)
- [x] Backend: UNIQUE constraint изменён с (user_id, schedule_entry_id) на (user_id, subject_name)
- [x] Backend: Alembic миграция e8f9a0b1c2d3 с дедупликацией данных (DISTINCT ON)
- [x] Backend: create_note() → upsert (возвращает 201 new / 200 updated)
- [x] Backend: GET /api/v1/notes/subject/{subject_name} — новый endpoint
- [x] Backend: 26 тестов notes (5 новых: upsert + subject endpoint)
- [x] Frontend: noteService.getNoteForSubject() вместо getNoteForEntry()
- [x] Frontend: LessonDetailModal — query по subject_name, cache invalidation через queryClient
- [x] Frontend: SchedulePage/ScheduleGrid/DayScheduleCard — noteSubjectNames Set вместо noteEntryIds
- [x] Frontend: MSW handler для GET /notes/subject/:subjectName
- [x] Fix: `.env` симлинк на сервере (docker compose не видел переменные при recreate)
- [x] Деплой на сервер — миграция применена, все контейнеры healthy, CI зелёный

### Code Review Implementation (ЗАВЕРШЕНА ✅) — 2026-02-11
13 исправлений из code review плана (P0-P2), все задеплоены на сервер.

#### P0 — Critical
- [x] P0-1: CASCADE DELETE → SET NULL на absences FK + добавлены subject_name/lesson_date для идентификации без entry
- [x] P0-1: lesson_notes FK тоже CASCADE → SET NULL
- [x] P0-1: Alembic миграция f1a2b3c4d5e6 с backfill из schedule_entries
- [x] P0-2: Убран StaticFiles mount `/uploads` (файлы только через auth endpoint)
- [x] P0-2: Убран `/uploads/` location из nginx.conf
- [x] P0-3: Content-Disposition header injection fix (urllib.parse.quote)
- [x] P0-4: LIKE wildcard injection fix (escape `%`, `_`, `\`)

#### P1 — High
- [x] P1-1: AbortSignal передаётся в noteService.createNote/updateNote
- [x] P1-2: schedule_group_id добавлен в Settings (убран getattr fallback)
- [x] P1-3: Redis authentication в docker-compose.prod.yml (--requirepass)
- [x] P1-4: Health endpoint проверяет DB (SELECT 1) и Redis (ping)

#### P2 — Medium
- [x] P2-1: DRY magic bytes ({**_IMAGE_SIGNATURES, ...})
- [x] P2-2: Удалён неиспользуемый aiopg
- [x] P2-3: python-jose → PyJWT (python-jose deprecated с 2021)
- [x] P2-4: void peTeacher → явный параметр в filterWeekSchedule
- [x] P2-5: Пагинация limit/offset на files и notes endpoints

#### Hotfix при деплое
- [x] alembic/env.py: psycopg2 → psycopg (psycopg2 ушёл с aiopg)
- [x] REDIS_PASSWORD добавлен в .env на сервере

### Remove User Limit (ЗАВЕРШЕНА ✅) — 2026-02-11
Снято ограничение MAX_USERS=2, регистрация открыта для всех одногруппников.
- [x] Удалена константа MAX_USERS и проверка лимита в register_user()
- [x] Удалён класс UserLimitException
- [x] Удалён тест test_register_max_users_limit
- [x] Обновлены docstrings (убраны упоминания "2 users", "pair mode")
- [x] Удалён комментарий про 2 пользователей из RegisterPage
- [x] Обновлена документация (CLAUDE.md, project_status.md, fastapi.md)

### SSL (HTTPS) (ЗАВЕРШЕНА ✅) — 2026-02-11
- [x] `nginx/nginx.conf` — 3 server-блока: HTTP (ACME challenge + 301 redirect), HTTPS www (301 redirect), HTTPS main (приложение)
- [x] `nginx/nginx.conf` — SSL directives, `http2 on`, HSTS (`max-age=31536000; includeSubDomains`)
- [x] `nginx/nginx.conf` — security headers продублированы в nested locations (nginx add_header inheritance fix)
- [x] `nginx/Dockerfile` — `EXPOSE 443`, healthcheck с HTTPS fallback
- [x] `docker-compose.prod.yml` — порт 443, certbot сервис (auto-renewal каждые 12ч), volumes `certbot_certs`/`certbot_webroot`
- [x] `.env.production.example` — `DOMAIN`, `CERTBOT_EMAIL`, `HTTPS_PORT`, `REDIS_PASSWORD`
- [x] `scripts/init-letsencrypt.sh` — bootstrap скрипт (DNS check → TLS params → self-signed → nginx start → real cert → reload)
- [x] Let's Encrypt сертификат получен (expires 2026-05-12)
- [x] Деплой на сервер — 5 контейнеров (db, redis, backend, nginx, certbot), все работают

### Backend Rebuild (2026-02-11)
- [x] Пересобран Docker образ backend (MAX_USERS лимит не применялся после git pull)
- [x] Контейнер backend пересоздан и запущен (healthy)
- [x] Проверено: `MAX_USERS` отсутствует в контейнере
- [x] Тестовая регистрация успешна (id: 3), тестовый пользователь удалён

### UI Improvements (2026-02-11)
- [x] ClassmatesPage: название группы `МБС-301-О-01` в заголовке
- [x] ClassmatesPage: общее количество одногруппников рядом с кнопкой "+"
- [x] ClassmatesPage: количество людей в каждой подгруппе
- [x] ClassmatesPage: адаптивный заголовок (`text-xl sm:text-2xl`)
- [x] SemestersPage: показывать "Семестр N" вместо полного названия
- [x] DashboardPage: убрана фраза "Что будем делать сегодня?"
- [x] formatLocation: парсинг формата API `"(6"` + `"113) Спортивный зал"` → `"6-113"`
- [x] formatLocation: очистка скобок из building, извлечение номера аудитории из room
- [x] nginx: location `/uploads/avatars/` для публичных аватарок одногруппников
- [x] docker-compose.prod.yml: volume `uploads_data` примонтирован в nginx (read-only)
- [x] 31 тест dateUtils (было 22, добавлено 9 для formatLocation)
- [x] Деплой на сервер — 3 коммита, nginx пересобран

### Attendance Logic Rewrite (2026-02-11)
Полная переработка логики посещаемости по плану `flickering-snuggling-moler.md`:
- [x] Backend: `planned_classes` добавлен в модель Subject (для учёта запланированных пар)
- [x] Backend: Alembic миграция `1f580bc1b2b5_add_planned_classes_to_subjects`
- [x] Backend: Attendance сервис переписан с фильтрацией по семестру (start_date/end_date)
- [x] Backend: Только завершённые пары (lesson_date < today OR end_time <= now)
- [x] Backend: Новые поля в AttendanceStats: `total_planned`, `total_completed`
- [x] Backend: Все attendance endpoints требуют `semester_id` параметр
- [x] Backend: 29 тестов посещаемости (было 22)
- [x] Frontend: AttendancePage с выбором семестра (dropdown как в SubjectsPage)
- [x] Frontend: Предупреждение если у семестра не заданы даты
- [x] Frontend: AttendanceStatsCard показывает "X из Y" (attended / total_planned)
- [x] Frontend: SubjectsPage с полем planned_classes в форме создания/редактирования
- [x] Frontend: Обновлены типы Subject и AttendanceStats
- [x] Frontend: Обновлены MSW handlers и тесты (357 тестов проходят)
- [x] Деплой на сервер — миграция применена, все контейнеры healthy

### Settings & Subgroup Filter (2026-02-11)
Настройки пользователя и фильтрация расписания по подгруппам:
- [x] Backend: `parse_subgroup_from_group_name()` в `data_mapper.py` — парсинг "МБС-301-О-01/1" → 1
- [x] Backend: `map_api_entry()` заполняет subgroup из group_name
- [x] Backend: 8 новых тестов парсера (82 всего)
- [x] Frontend: `settingsStore.ts` — Zustand store (subgroup, peTeacher, localStorage persistence)
- [x] Frontend: `subgroupFilter.ts` — filterBySubgroup, getAlternateEntryForSlot, filterWeekBySubgroup
- [x] Frontend: `SettingsPage.tsx` — страница /settings (подгруппа radio, физра select, ЛК ОмГУ заглушка)
- [x] Frontend: `ScheduleGrid.tsx` — индикатор "!" с Popover для альтернативных пар другой подгруппы
- [x] Frontend: `SchedulePage.tsx` — интеграция фильтров (peTeacher + subgroup), передача allEntries
- [x] Frontend: `DashboardPage.tsx` — интеграция фильтров
- [x] Frontend: `PeTeacherSelect.tsx` — рефакторинг на settingsStore
- [x] Frontend: `peTeacherFilter.ts` — убраны localStorage функции (теперь в settingsStore)
- [x] Frontend: QuickActions — добавлен пункт "Настройки" (Settings icon, gray)
- [x] Frontend: 359 тестов проходят
- [x] TypeScript, ESLint, build — всё чисто

### LK Parser (2026-02-12)
Парсинг личного кабинета ОмГУ (https://eservice.omsu.ru/sinfo/):
- [x] Backend: модели `LkCredentials`, `SessionGrade`, `SemesterDiscipline`
- [x] Backend: Fernet encryption для credentials (`utils/crypto.py`)
- [x] Backend: `LkParser` — HTTP клиент с OAuth2 авторизацией (`parser/lk_parser.py`)
- [x] Backend: сервис `lk.py` — credentials CRUD, sync, upsert grades/disciplines
- [x] Backend: роутер `/api/v1/lk` — status, credentials, verify, sync, grades, disciplines
- [x] Backend: Alembic миграция `2a3b4c5d6e7f_add_lk_tables`
- [x] Backend: 51 тест (crypto: 6, API: 29, parser: 16)
- [x] 418 тестов backend — все проходят

### LK Integration — Frontend (ЗАВЕРШЕНА ✅) — 2026-02-12
Полная интеграция ЛК в приложение по плану `delightful-inventing-peach.md`:
- [x] Backend: `total_hours` поле в модели Subject (часы из учебного плана ЛК)
- [x] Backend: Alembic миграция `488c2925b15c_add_total_hours_to_subjects`
- [x] Backend: `POST /api/v1/lk/import` — импорт семестров и предметов из ЛК в приложение
- [x] Backend: `import_to_app()` в lk.py — создание/обновление Semester и Subject из SemesterDiscipline
- [x] Backend: `LkImportResult` схема (semesters_created/updated, subjects_created/updated)
- [x] Frontend: `lkService.ts` — полноценный сервис (getStatus, saveCredentials, verify, sync, importToApp, getGrades, getSessions)
- [x] Frontend: `types/lk.ts` — LkStatus, LkCredentials, SessionGrade, SemesterDiscipline, LkImportResult
- [x] Frontend: `SettingsPage.tsx` — рабочая секция ЛК (verify/save/sync credentials, status display, disconnect)
- [x] Frontend: `SemestersPage.tsx` — кнопка "Импорт из ЛК" с confirm modal
- [x] Frontend: `SubjectsPage.tsx` — отображение и редактирование total_hours
- [x] Frontend: `SubjectProgressCard.tsx` — показывает total_hours в заголовке
- [x] Frontend: `GradesPage.tsx` — новая страница /grades (зачётка)
  - Статистика: всего оценок, средний балл, % отличных
  - Группировка по сессиям (SessionGroup)
  - Цветные badges по результату (отлично=green, хорошо=blue, удовл=yellow, неуд=red, зачтено=emerald)
  - Фильтр по сессиям
  - Кнопка синхронизации
- [x] Frontend: `QuickActions.tsx` — пункт "Зачётка" (Award icon, violet)
- [x] Frontend: `dateUtils.ts` — `formatDistanceToNow()` для относительного времени
- [x] Frontend: Маршрут /grades в App.tsx
- [x] Деплой на сервер — 18 миграций применено, все контейнеры healthy

---

## Что в работе

Нет активных задач.

### Следующие задачи (приоритет):
1. ~~**SSL (HTTPS)** — Let's Encrypt (P0)~~ ✅
2. **Бэкапы PostgreSQL** — cron + pg_dump (P0)
3. **05-ics-export** — экспорт в .ics (P2)
4. **02-push-notifications** — push-уведомления (P1, зависит от PWA ✅)

### Деплой
✅ **Приложение задеплоено и работает**: https://studyhelper1.ru
- Домен: `studyhelper1.ru` (DNS A → 89.110.93.63)
- SSL: Let's Encrypt, auto-renewal certbot (каждые 12ч)
- HTTP → HTTPS redirect, www → apex redirect
- HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- 5 контейнеров: db, redis, backend, nginx, certbot
- 18 миграций применены
- Redis с аутентификацией (REDIS_PASSWORD)

---

## Что отложено (на будущее)

### Отдельный PR (из Code Review)
- httpOnly cookies вместо localStorage
- Механизм отзыва JWT
- ~~Docker production config~~ ✅

---

## Известные проблемы

### Windows + Docker + asyncpg
На Windows есть критические проблемы с asyncpg при подключении к PostgreSQL в Docker.
**Решение**: Использовать локальный PostgreSQL вместо Docker на Windows.

### Windows + Vite + localhost
Vite на Windows может не слушать на правильном адресе из-за IPv6/IPv4 резолвинга.
**Решение**: Явно указать `host: '127.0.0.1'` в vite.config.ts

### ~~ESLint: pre-existing ошибки в shadcn/ui~~ ✅ РЕШЕНО
~~3 ошибки в shadcn/ui компонентах~~ — `src/components/ui` добавлен в globalIgnores ESLint.

### Vitest: процесс подвисает при завершении (Windows)
При `vitest run` на Windows процесс не завершается после прохождения всех тестов (MSW + jsdom удерживают сокеты).
**Решение**: Использовать `pool: 'forks'` в конфиге + `timeout` при запуске из CI. Все 114 тестов проходят корректно, подвисание только при cleanup.

### Vitest: OOM при cleanup (Windows)
При `vitest run` на Windows воркер падает с OOM (`JavaScript heap out of memory`) на ~4GB после прохождения всех тестов (Vitest 4.0.18, issue #9560).
**Решение**: Создан Claude Code агент `.claude/agents/test-runner.md` — запускает тесты в фоне, парсит вывод, убивает зависший процесс через TaskStop. Все 348+ тестов проходят корректно, OOM только при cleanup.

### Production: Nginx healthcheck медленный
Nginx healthcheck использует `wget`, который может долго стартовать (>30 сек). Контейнер в статусе `health: starting` дольше ожидаемого.
**Статус**: Не критично, приложение работает корректно. Можно оптимизировать healthcheck командой (curl вместо wget).

### Production: API docs недоступны
`/api/v1/docs` возвращает 404 на production сервере.
**Статус**: Возможно, отключены в production конфигурации. Требует проверки.

---

## Архитектурные заметки

- **Модель доступа**: все пользователи видят общие данные (расписание, предметы, работы), WorkStatus/Notes/Attendance создаётся для каждого
- **История статусов**: WorkStatusHistory автоматически при изменении статуса
- **Аутентификация**: JWT (access 15min, refresh 7days), открытая регистрация
- **База данных**: PostgreSQL + aiosqlite для тестов
- **Расписание**: lesson_date для конкретных дат занятий
- **Парсер**: HTTP API (httpx) + SHA-256 хеширование для отслеживания изменений
- **API расписания**: `https://eservice.omsu.ru/schedule/backend/schedule/group/{group_id}`
- **Frontend**: Vite + React 19 + TypeScript + Tailwind v4 + Zustand + React Query
- **Календарь**: react-day-picker v9 + @radix-ui/react-popover
- **Security**: rate limiting (slowapi), security headers, magic bytes validation, streaming uploads, path traversal protection, LIKE wildcard escape, Content-Disposition URL-encoding, no public StaticFiles mount, Redis auth
- **Frontend infrastructure**: ErrorBoundary, shared Modal (accessible), sonner toasts, AbortController signals, token refresh mutex
- **Frontend тесты**: Vitest + @testing-library/react + MSW для моков API
- **PWA**: vite-plugin-pwa (generateSW), registerType: prompt, NetworkFirst для API, offline.html fallback
- **Dashboard виджеты**: TodayScheduleWidget, DeadlinesWidget, QuickActions — отдельные компоненты в `components/dashboard/`
- **Clickable schedule**: LessonDetailModal с работами и заметками, onClick/onEntryClick на LessonCard/ScheduleGrid/TodayScheduleWidget
- **Progress bars**: ProgressBar (a11y, size variants), SubjectProgressCard, SemesterProgressWidget (top-3 lowest), calculateSemesterProgress в progressUtils
- **File upload**: File модель (immutable), FileDropzone (HTML5 DnD), FileList, magic bytes validation, StreamingResponse для download, path traversal protection
- **Lesson notes**: LessonNote модель (one per subject per user), upsert POST (201/200), GET /subject/{name}, NoteEditor (autosave debounce 500ms), NoteCard, NotesPage, LessonDetailModal query по subject_name с cache invalidation
- **Semester timeline**: start_date/end_date на Semester (nullable), TimelineBar (CSS positioning via left%), TimelineMarker (Popover tooltips), getPositionPercent/getMonthLabels/getSemesterProgress утилиты, TimelinePage с фильтрами, SemesterTimelineWidget на Dashboard
- **Dark theme**: ThemeMode (light/dark/system), FOUC prevention (inline script), cycling toggle (Sun/Moon/Monitor), localStorage persistence, .dark CSS class, theme-color meta update, dark: variants для hardcoded цветов
- **Production Docker**: multi-stage builds (uv для backend, node для frontend), nginx reverse proxy, rate limiting (nginx + slowapi), --proxy-headers для корректного client IP, memory limits ~1.3GB total, PostgreSQL tuning (shared_buffers=256MB), Redis LRU (128mb)
- **Schedule auto-sync**: APScheduler 3.x AsyncIOScheduler в lifespan FastAPI, IntervalTrigger(hours=6, jitter=60), misfire_grace_time=3600, Redis distributed lock (non-blocking, TTL 600s, LockNotOwnedError handling), Redis auto-reconnect (ping healthcheck), initial sync в entrypoint.sh (если snapshot нет), configurable via SCHEDULE_SYNC_ENABLED/SCHEDULE_UPDATE_INTERVAL_HOURS
- **SSL/TLS**: Let's Encrypt certbot (webroot mode), auto-renewal каждые 12ч, nginx 3 server-блока (HTTP redirect + HTTPS www redirect + HTTPS main), http2, HSTS, bootstrap скрипт `scripts/init-letsencrypt.sh` (self-signed → real cert)
- **Settings**: settingsStore (Zustand) с localStorage persistence, subgroup фильтрация (filterBySubgroup), SettingsPage (/settings) с секциями (подгруппа, физра, ЛК)
- **Subgroup filtering**: Parser извлекает subgroup из поля `subgroupName` API (e.g. "МБС-301-О-01/1" → 1), ScheduleGrid показывает "!" на пустых ячейках где есть пара для другой подгруппы, popover с деталями
- **LK Parser**: OAuth2-based auth (CSRF + form-login + redirects), httpx cookie persistence, Fernet encryption (PBKDF2HMAC 1.2M iterations), SessionGrade/SemesterDiscipline upsert, verify без сохранения credentials
- **LK Integration**: import_to_app() создаёт Semester/Subject из SemesterDiscipline, total_hours из ЛК, GradesPage со статистикой и группировкой по сессиям

---

## Метрики

| Метрика | Значение |
|---------|----------|
| Тестов backend | 418 |
| Тестов frontend | 359 |
| Покрытие тестами | ~80% |
| API endpoints | ~70 |
| Моделей | 16 |
| Миграций | 18 |
| Линтер backend | ✅ Ruff проходит |
| Линтер frontend | ✅ ESLint проходит (shadcn/ui исключён из линтинга) |
| Frontend тесты | ✅ Vitest проходит (359 тестов) |
| Frontend build | ✅ TypeScript + Vite |
| Frontend страниц | 14 (Login, Register, Dashboard, Schedule, Subjects, Works, Semesters, Classmates, Files, Attendance, Notes, Timeline, Settings, Grades) |
