# Статус проекта StudyHelper

## Последнее обновление
- **Дата**: 2026-02-08
- **Сессия**: Реализация 10-lesson-notes (заметки к парам)

## Общий прогресс
**Фаза**: Post-MVP реализация
**Прогресс**: MVP 100% завершён. 01-PWA реализована. 04-dashboard-widget реализован. 06-clickable-schedule реализован. 07-progress-bars реализован. 03-file-upload-ui реализован. 08-attendance реализован. 10-lesson-notes реализован.

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
- [x] GitHub Actions CI (backend lint+test + frontend lint+build)

### Backend (ЗАВЕРШЁН)
- [x] Инициализация проекта (pyproject.toml, uv)
- [x] Конфигурация (pydantic-settings)
- [x] База данных (SQLAlchemy 2.0 async)
- [x] Alembic миграции (12 миграций применено)

#### Модули:
| Модуль | Модель | Схемы | Сервис | Роутер | Тесты |
|--------|--------|-------|--------|--------|-------|
| Auth | ✅ User | ✅ | ✅ | ✅ | ✅ 16 |
| Semesters | ✅ | ✅ | ✅ | ✅ | ✅ 17 |
| Subjects | ✅ | ✅ | ✅ | ✅ | ✅ 18 |
| Works | ✅ Work, WorkStatus, WorkStatusHistory | ✅ | ✅ | ✅ | ✅ 23 |
| Teachers | ✅ | ✅ | ✅ | ✅ | ✅ 20 |
| University | ✅ Department, Building | ✅ | ✅ | ✅ | ✅ 28 |
| Classmates | ✅ | ✅ | ✅ | ✅ | ✅ 20 |
| Schedule | ✅ ScheduleEntry, ScheduleSnapshot | ✅ | ✅ | ✅ | ✅ 24+11 |
| Parser | ✅ | ✅ | ✅ | CLI | ✅ 74 |
| Uploads | — | ✅ | ✅ | ✅ | ✅ 11 |
| Files | ✅ File | ✅ | ✅ | ✅ | ✅ 21 |
| Attendance | ✅ Absence | ✅ | ✅ | ✅ | ✅ 22 |
| Notes | ✅ LessonNote | ✅ | ✅ | ✅ | ✅ 21 |

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
- [x] SubjectsPage ✅
- [x] WorksPage ✅
- [x] SemestersPage ✅ (CRUD для семестров)
- [x] ClassmatesPage ✅ (CRUD, контакты, санитизация Telegram)

### Frontend тесты (ЗАВЕРШЁН ✅)
- [x] Тестовая инфраструктура: Vitest + @testing-library/react + MSW
- [x] Тесты утилит: dateUtils (22), errorUtils (13), constants (6)
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
- [x] Backend: UniqueConstraint(user_id, schedule_entry_id), indexes (user_id+lesson_date, user_id+subject_name)
- [x] Backend: схемы (LessonNoteCreate, LessonNoteUpdate, LessonNoteResponse)
- [x] Backend: сервис (create_note, update_note, delete_note, get_notes с фильтрами, get_note_for_entry)
- [x] Backend: роутер (POST / 201, GET /, GET /entry/{id}, PUT /{id}, DELETE /{id} 204)
- [x] Backend: Alembic миграция add_lesson_notes_table
- [x] Backend: 21 тест (create: 6, get_notes: 5, get_note_for_entry: 3, update: 4, delete: 3)
- [x] Frontend: типы (LessonNote, LessonNoteCreate, LessonNoteUpdate)
- [x] Frontend: сервис (noteService: getNotes, getNoteForEntry, createNote, updateNote, deleteNote)
- [x] Frontend: NoteEditor (autosave debounce 500ms, status indicator, char counter 2000, disabled)
- [x] Frontend: NoteCard (subject/date, content preview 150 chars, expand/collapse, delete)
- [x] Frontend: NotesPage (search debounce 300ms, subject filter, NoteCard list, delete confirm modal)
- [x] Frontend: LessonDetailModal — рефакторинг: textarea+save заменён на NoteEditor с autosave
- [x] Frontend: LessonCard — иконка StickyNote (amber-500) при наличии заметки (hasNote prop)
- [x] Frontend: ScheduleGrid, DayScheduleCard, SchedulePage — noteEntryIds Set из API
- [x] Frontend: маршрут /notes в App.tsx, пункт "Заметки" (StickyNote, text-yellow-500) в QuickActions
- [x] Frontend: MSW handlers + testLessonNotes data
- [x] Frontend: 23 новых теста (NoteEditor: 10, NoteCard: 5, NotesPage: 8) + обновлены LessonDetailModal тесты (17)
- [x] TypeScript, ESLint, build — всё чисто

---

## Что в работе

Нет активных задач. 10-lesson-notes реализован, ожидает коммит.

### Следующие задачи (приоритет):
1. ~~**01-PWA** — manifest, service worker, оффлайн (P0)~~ ✅
2. ~~**04-dashboard-widget** — виджеты Dashboard (P1)~~ ✅
3. ~~**06-clickable-schedule** — кликабельные элементы расписания (P1)~~ ✅
4. ~~**07-progress-bars** — прогресс-бары по предметам (P2)~~ ✅
5. ~~**03-file-upload-ui** — UI загрузки файлов (P1)~~ ✅
6. ~~**08-attendance** — посещаемость (P2)~~ ✅
7. ~~**10-lesson-notes** — заметки к парам (P2)~~ ✅
8. **09-dark-theme** — тёмная тема (P2)
9. **05-ics-export** — экспорт в .ics (P2)
10. **02-push-notifications** — push-уведомления (P1, зависит от PWA ✅)
11. **11-semester-timeline** — timeline семестра (P3)

### Деплой
Отложен до разбирательства с сервером.

---

## Что отложено (на будущее)

### Отдельный PR (из Code Review)
- httpOnly cookies вместо localStorage
- Механизм отзыва JWT
- Docker production config

---

## Известные проблемы

### Windows + Docker + asyncpg
На Windows есть критические проблемы с asyncpg при подключении к PostgreSQL в Docker.
**Решение**: Использовать локальный PostgreSQL вместо Docker на Windows.

### Windows + Vite + localhost
Vite на Windows может не слушать на правильном адресе из-за IPv6/IPv4 резолвинга.
**Решение**: Явно указать `host: '127.0.0.1'` в vite.config.ts

### ESLint: pre-existing ошибки в shadcn/ui
3 ошибки в shadcn/ui компонентах (button.tsx, input.tsx, label.tsx) — не связаны с нашим кодом.
- `react-refresh/only-export-components` в button.tsx
- `@typescript-eslint/no-empty-object-type` в input.tsx и label.tsx

### Vitest: процесс подвисает при завершении (Windows)
При `vitest run` на Windows процесс не завершается после прохождения всех тестов (MSW + jsdom удерживают сокеты).
**Решение**: Использовать `pool: 'forks'` в конфиге + `timeout` при запуске из CI. Все 114 тестов проходят корректно, подвисание только при cleanup.

### Vitest: OOM в watch mode (Windows)
При `npm run test` (watch mode) воркер Vitest падает с OOM (`JavaScript heap out of memory`) на ~4GB после прохождения всех тестов.
**Решение**: Использовать `npx vitest run` вместо watch mode. Тесты проходят корректно, OOM только при watch mode cleanup.

---

## Архитектурные заметки

- **Парный режим**: два пользователя видят все данные, WorkStatus создаётся для каждого
- **История статусов**: WorkStatusHistory автоматически при изменении статуса
- **Аутентификация**: JWT (access 15min, refresh 7days), макс 2 пользователя
- **База данных**: PostgreSQL + aiosqlite для тестов
- **Расписание**: lesson_date для конкретных дат занятий
- **Парсер**: HTTP API (httpx) + SHA-256 хеширование для отслеживания изменений
- **API расписания**: `https://eservice.omsu.ru/schedule/backend/schedule/group/{group_id}`
- **Frontend**: Vite + React 19 + TypeScript + Tailwind v4 + Zustand + React Query
- **Календарь**: react-day-picker v9 + @radix-ui/react-popover
- **Security**: rate limiting (slowapi), security headers, magic bytes validation, streaming uploads, path traversal protection
- **Frontend infrastructure**: ErrorBoundary, shared Modal (accessible), sonner toasts, AbortController signals, token refresh mutex
- **Frontend тесты**: Vitest + @testing-library/react + MSW для моков API
- **PWA**: vite-plugin-pwa (generateSW), registerType: prompt, NetworkFirst для API, offline.html fallback
- **Dashboard виджеты**: TodayScheduleWidget, DeadlinesWidget, QuickActions — отдельные компоненты в `components/dashboard/`
- **Clickable schedule**: LessonDetailModal с работами и заметками, onClick/onEntryClick на LessonCard/ScheduleGrid/TodayScheduleWidget
- **Progress bars**: ProgressBar (a11y, size variants), SubjectProgressCard, SemesterProgressWidget (top-3 lowest), calculateSemesterProgress в progressUtils
- **File upload**: File модель (immutable), FileDropzone (HTML5 DnD), FileList, magic bytes validation, StreamingResponse для download, path traversal protection
- **Lesson notes**: LessonNote модель (one per entry per user), NoteEditor (autosave debounce 500ms), NoteCard, NotesPage, LessonDetailModal интеграция через useQuery

---

## Метрики

| Метрика | Значение |
|---------|----------|
| Тестов backend | 328 |
| Тестов frontend | 279 |
| Покрытие тестами | ~80% |
| API endpoints | ~64 |
| Моделей | 15 |
| Миграций | 12 |
| Линтер backend | ✅ Ruff проходит |
| Линтер frontend | ✅ ESLint проходит (кроме shadcn/ui) |
| Frontend тесты | ✅ Vitest проходит (279 тестов) |
| Frontend build | ✅ TypeScript + Vite |
| Frontend страниц | 11 (Login, Register, Dashboard, Schedule, Subjects, Works, Semesters, Classmates, Files, Attendance, Notes) |
