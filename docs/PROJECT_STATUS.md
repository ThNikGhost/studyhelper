# Статус проекта StudyHelper

## Общий прогресс
- **Фаза**: Production
- **Прогресс**: MVP 100%. Все post-MVP фичи реализованы. Production с SSL на https://studyhelper1.ru.
- **Дата обновления**: 2026-03-14 (fix: full code review audit — 22 fixes, коммит 7850ab3)

## Backend модули

| Модуль | Модель | Схемы | Сервис | Роутер | Тесты |
|--------|--------|-------|--------|--------|-------|
| Auth | User (+settings, +hidden_subjects dict) | UserSettingsUpdate | CRUD + settings | +PATCH /me/settings | 37 |
| Semesters | +start/end_date | +Timeline | +timeline | +timeline | 26 |
| Subjects | +planned_classes, +total_hours | +lesson_types (computed) | +_get_subject_lesson_types | — | 20 |
| Works | Work (+deadline_has_time, +diff_credit/colloquium types), WorkStatus, WorkStatusHistory | — | — | — | 23 |
| Teachers | — | — | — | — | 20 |
| University | Department, Building | — | — | — | 28 |
| Classmates | +ClassmateDetail (per-user) | +ClassmateDetailUpsert/Response | +upsert_details | +PUT /{id}/details | 26 |
| Schedule | ScheduleEntry, ScheduleSnapshot | — | — | — | 35 |
| Parser | +subgroup parsing, +ауд. prefix | — | — | CLI | 84 |
| Uploads | — | — | — | — | 11 |
| Files | File | +FileUpdateRequest | +update_file (async I/O) | +PATCH /{id} | 24 |
| Attendance | Absence | +total_planned/completed | semester filter | — | 29 |
| Notes | LessonNote | — | upsert | — | 26 |
| LK | LkCredentials, SessionGrade, SemesterDiscipline | +LkImportResult | +import_to_app | +/import | 51 |
| Telegram | TelegramLink | Status/LinkCode/Notifications | link/unlink/notifications | webhook+REST | ~50 (+schedule_utils) |
| Calendar | CalendarFeed | Status/CreateResponse | token CRUD + ICS gen | status/enable/disable/feed | 27 |
| Widget | WidgetApiKey | Status/Create/NextLesson/TodaySchedule | token CRUD + next lesson + today schedule | status/enable/disable/next-lesson/today | 43 |

## Frontend

13 страниц: Login, Register, Dashboard, Schedule, Subjects, Works, Semesters, Classmates, Files, Attendance, Timeline, Settings, Grades. (Notes убрана из навигации, доступна через LessonDetailModal)

**Full code review audit (2026-03-14, коммит 7850ab3):**
- CORS: добавлен `PATCH` в allow_methods + `expose_headers: ["X-Request-ID"]`
- Файловый I/O: `save_file`/`save_avatar`/`delete_file` → `asyncio.to_thread()` (non-blocking)
- `create_work`: batch flush (1 DB round-trip вместо N)
- Dead code: удалён `update_file_category()`, убрана двойная валидация FileCategory enum
- 5x `type: ignore` → `assert is not None` (proper narrowing)
- App.tsx: DRY рефактор — `ProtectedLayout` с `<Outlet />` (-120 строк)
- WorkFilesModal: AbortController (cancel on unmount) + stale closure fix
- authStore: `isLoading: false` при logout
- Config: валидация `telegram_webhook_url`; database: `pool_recycle=3600`
- CI: frontend тесты добавлены, Node.js 20→22
- Infra: Redis healthcheck `$$REDIS_PASSWORD`, nginx healthcheck `127.0.0.1`
- "до 50 MB" → динамический `MAX_FILE_SIZE_MB` в двух компонентах
- Non-null assertions убраны (3 страницы)

**Bugfixes (2026-03-02, коммит b4348b2):**
- dateUtils: `formatDeadline` + `getDeadlineColor` — calendar-day сравнение вместо `Math.ceil(diffMs/24h)`, фикс "Завтра" вместо "Сегодня" для дедлайнов 23:59 (date-only)
- AttendancePage: `filteredStats` пересчитывает строку физкультуры из `filteredEntries` при активном `peTeacher` — статистика показывает ~6 занятий вместо 20
- DeadlinesWidget: `getUrgency` возвращает `null` при `diffDays > 7`, работы дальше 7 дней не попадают в "На неделе"
- Тесты: +2 регрессионных в `dateUtils.test.ts`; обновлён "max 8 items" + добавлен "beyond 7 days" в `DeadlinesWidget.test.tsx`; итого 406 frontend тестов (3 pre-existing SchedulePage failures)

**UI-улучшения (2026-02-23):**
- FilesPage: inline редактирование категории — карандаш при hover, select, Escape/blur для отмены
- FilesPage: кнопка "Открыть в браузере" (ExternalLink) для PDF и изображений без принудительного скачивания
- fileService: `updateFileCategory()`, `openFile()` (blob → `window.open`)
- fileUtils: `canOpenInBrowser()` для PDF + image/*
- Backend: `PATCH /files/{id}` (owner-only), 3 новых теста, итого 668 тестов
- AttendancePage: фильтр журнала по частично скрытым типам занятий (hiddenSubjects per-type) и преподавателю физкультуры (peTeacher) — коммит d0ef93b
- FileList.test.tsx: обёртка в QueryClientProvider (useQueryClient появился после добавления редактирования категории)

**Code review fixes (2026-02-21):**
- schedule_filters: `v is not None` — пустой `[]` больше не трактуется как "скрыть всё"
- scheduler: Prometheus метка `failure` вместо `success` в else-ветке
- attendance/omsu_parser: `date.today()` → `datetime.now(OMSK_TZ).date()`
- crypto: `lru_cache` на `get_fernet()` — не блокирует event loop
- retry: обработка `HTTPStatusError` 502/503/504 как retryable
- notifications+scheduler: `send_schedule_changed_locked()` с Redis-замком
- academics `/deadlines`: фильтрует hidden_subjects
- work.py: `changed_by_id: Mapped[int | None]` (правильная nullable FK)
- classmate: индекс `ix_classmate_details_classmate_id` + миграция `k1l2m3n4o5p6`
- routers/lk: logger на уровень модуля; services/lk: `db.flush()` вместо промежуточных `db.commit()`
- api.ts: `processQueue` перед редиректом (утечка памяти); fileService: `signal` параметр
- WorksPage: batch modal остаётся открытым при частичной ошибке
- Dockerfile + docker-compose.prod.yml: `localhost` → `127.0.0.1`
- Android: executor в companion object; `>=` для занятия, начавшегося ровно сейчас

**Предыдущие UI-улучшения (2026-02-21):**
- FilesPage: multiple file upload — выбор нескольких файлов через dialog/drag-drop, очередь с удалением, кнопка "Загрузить (N)", суммарный прогресс, один toast

**Предыдущие UI-улучшения (2026-02-19):**
- SettingsPage: per-lesson-type subject hiding — colored type chips (Лек/Прак/Лаб) per subject
- Schedule filtering: hide specific lesson types while keeping others visible
- Works/Subjects/Attendance: only fully hidden subjects (all types) are filtered out
- WorksPage: split date/time deadline input, optional time with "date-only" hint
- WorksPage: batch mode — add multiple works at once (single/batch toggle)
- SchedulePage: hidden subjects filtered from alternate entry "!" indicators

React.lazy() code splitting, PWA (offline fallback, update prompt with hourly SW checks + fallback reload), dark theme (system/light/dark).

## Деплой
- **URL**: https://studyhelper1.ru (89.110.93.63)
- **SSL**: Let's Encrypt, certbot auto-renewal (12h)
- **Контейнеры**: db, redis, backend, nginx, certbot (5 шт.)
- **Миграции**: 28 применено (все задеплоены, включая `l2m3n4o5p6q7`)
- **Sync**: APScheduler каждые 6ч + Redis distributed lock
- **Backups**: pg_dump daily cron (3:00 UTC), gzip, 7-day rotation

## Что в работе

Все задачи B1-B13, F1-F6, SEC-1, SEC-1.1, CD завершены и задеплоены. История изменений — в `DECISIONS.md` и git log.

### Следующие задачи (приоритет):
- (Фаза 3) httpOnly cookies, JWT blacklist
- (Будущее) CSP unsafe-inline removal

## Что отложено
- httpOnly cookies вместо localStorage (Security Audit Phase 3)
- JWT blacklist через Redis (Security Audit Phase 3)
- CSP: убрать unsafe-inline (hash-based или vite-csp-guard)

## Известные проблемы

### Windows + Docker + asyncpg
Критические проблемы asyncpg → PostgreSQL в Docker на Windows.
**Решение**: Локальный PostgreSQL.

### Windows + Vite + localhost
IPv6/IPv4 резолвинг. **Решение**: `host: '127.0.0.1'` в vite.config.ts.

### Vitest: зависание при cleanup (Windows)
Процесс зависает после тестов, 4GB+ RAM (Vitest bug #9560).
**Решение**: `/test` skill (test-runner агент с принудительным kill).

### Production: API docs недоступны
`/api/v1/docs` → 404. Требует проверки.

## Архитектура

### Core
- **Модель доступа**: общие данные (расписание, предметы, работы, заметки) + per-user (WorkStatus, Attendance)
- **Auth**: JWT (access 15min, refresh 7days), PyJWT, открытая регистрация
- **DB**: PostgreSQL + aiosqlite (тесты), Alembic миграции
- **Parser**: httpx + SHA-256 change detection, API `eservice.omsu.ru/schedule/backend/schedule/group/{group_id}`
- **LK Parser**: OAuth2 auth, Fernet encryption (PBKDF2HMAC), import_to_app() для Semester/Subject
- **Frontend**: Vite + React 19 + TS + Tailwind v4 + shadcn/ui + Zustand + TanStack Query
- **PWA**: vite-plugin-pwa (generateSW, NetworkFirst API, offline.html)
- **Settings sync**: useUserSettings (TanStack Query optimistic) + useLocalSettingsStore fallback

### Security
- Rate limiting (nginx 30r/s + slowapi), security headers (HSTS, CSP, X-Frame-Options)
- Magic bytes validation, streaming uploads, path traversal protection
- LIKE wildcard escape, Content-Disposition URL-encoding, Redis auth
- Token refresh mutex, AbortController signals

### Infrastructure
- **Docker**: multi-stage builds (uv backend, node frontend), nginx reverse proxy, ~1.3GB total
- **SSL**: Let's Encrypt certbot (webroot), 3 nginx server-blocks, http2, HSTS
- **Auto-sync**: APScheduler 3.x, IntervalTrigger(6h, jitter=60), Redis lock (TTL 600s)
- **Telegram**: aiogram 3.25 webhook mode, conditional init (token-gated), 9 commands + reply keyboard, CronTrigger notifications, Redis lock for notification jobs
- **Calendar Feed**: icalendar 7.x, per-user token URL auth, schedule + deadline events, subgroup/PE filtering, REFRESH-INTERVAL 6h
- **Widget API**: per-user token query param auth, next lesson + today schedule JSON endpoints, 7-day lookahead, subgroup/PE filtering, Scriptable JS widget with offline cache
- **Observability**: structlog (JSON prod / ConsoleRenderer dev), X-Request-ID, Prometheus metrics (/metrics), Sentry error tracking (optional, DSN-gated)
- **CI**: GitHub Actions (backend lint+test, frontend lint+test+build, Android conditional release/debug build on tag)
- **Android Widget**: Native APK v1.3.2 (AGP 9.0.0, Kotlin built-in, Gradle 9.3.1), 4×2 AppWidgetProvider + RemoteViews, system Chronometer real-time countdown + AlarmManager exact refresh at lesson start, WorkManager 30min refresh, HttpURLConnection + org.json (no external deps), SharedPreferences (API key + 24h JSON cache), release-signed APK via GitHub Releases (`android/v*` tags), Gradle-native signing with base64 keystore Secret

## Метрики

| Метрика | Значение |
|---------|----------|
| Backend тестов | 675 |
| Frontend тестов | 408 (3 pre-existing SchedulePage failures) |
| Покрытие | ~80% |
| API endpoints | ~76 |
| Моделей | 19 |
| Миграций | 27 |
| Frontend страниц | 13 |
| Линтеры | Ruff + ESLint clean |
| Build | TypeScript + Vite clean |
| Android APK | ~3.8 MB (debug) |
