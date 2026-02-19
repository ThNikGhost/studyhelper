# Статус проекта StudyHelper

## Общий прогресс
- **Фаза**: Production
- **Прогресс**: MVP 100%. Все post-MVP фичи реализованы. Production с SSL на https://studyhelper1.ru.
- **Дата обновления**: 2026-02-19 (fix Android widget countdown going negative — precise timing + AlarmManager refresh)

## Backend модули

| Модуль | Модель | Схемы | Сервис | Роутер | Тесты |
|--------|--------|-------|--------|--------|-------|
| Auth | User (+settings) | UserSettingsUpdate | CRUD + settings | +PATCH /me/settings | 21 |
| Semesters | +start/end_date | +Timeline | +timeline | +timeline | 26 |
| Subjects | +planned_classes, +total_hours | — | — | — | 18 |
| Works | Work, WorkStatus, WorkStatusHistory | — | — | — | 23 |
| Teachers | — | — | — | — | 20 |
| University | Department, Building | — | — | — | 28 |
| Classmates | — | — | — | — | 20 |
| Schedule | ScheduleEntry, ScheduleSnapshot | — | — | — | 35 |
| Parser | +subgroup parsing, +ауд. prefix | — | — | CLI | 84 |
| Uploads | — | — | — | — | 11 |
| Files | File | — | — | — | 21 |
| Attendance | Absence | +total_planned/completed | semester filter | — | 29 |
| Notes | LessonNote | — | upsert | — | 26 |
| LK | LkCredentials, SessionGrade, SemesterDiscipline | +LkImportResult | +import_to_app | +/import | 51 |
| Telegram | TelegramLink | Status/LinkCode/Notifications | link/unlink/notifications | webhook+REST | ~40 |
| Calendar | CalendarFeed | Status/CreateResponse | token CRUD + ICS gen | status/enable/disable/feed | 27 |
| Widget | WidgetApiKey | Status/Create/NextLesson/TodaySchedule | token CRUD + next lesson + today schedule | status/enable/disable/next-lesson/today | 43 |

## Frontend

13 страниц: Login, Register, Dashboard, Schedule, Subjects, Works, Semesters, Classmates, Files, Attendance, Timeline, Settings, Grades. (Notes убрана из навигации, доступна через LessonDetailModal)

**Последние UI-улучшения (2026-02-18):**
- Вкладка "Семестры" убрана из Quick Actions на дашборде (роут `/semesters` сохранён)
- Селектор семестра в SubjectsPage: формат "6 семестр 2025/2026", бейдж "Текущий", даты под селектором
- Кнопки edit/delete в карточке предмета: убран absolute overlay, кнопки встроены в заголовок карточки
- `formatIsoDate` добавлен в `dateUtils.ts`

React.lazy() code splitting, PWA (offline fallback, update prompt), dark theme (system/light/dark).

## Деплой
- **URL**: https://studyhelper1.ru (89.110.93.63)
- **SSL**: Let's Encrypt, certbot auto-renewal (12h)
- **Контейнеры**: db, redis, backend, nginx, certbot (5 шт.)
- **Миграции**: 22 применено
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
- **Модель доступа**: общие данные (расписание, предметы, работы) + per-user (WorkStatus, Notes, Attendance)
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
- **CI**: GitHub Actions (backend lint+test, frontend lint+build, Android conditional release/debug build on tag)
- **Android Widget**: Native APK (AGP 9.0.0, Kotlin built-in, Gradle 9.3.1), 4×2 AppWidgetProvider + RemoteViews, system Chronometer real-time countdown + AlarmManager exact refresh at lesson start, WorkManager 30min refresh, HttpURLConnection + org.json (no external deps), SharedPreferences (API key + 24h JSON cache), release-signed APK via GitHub Releases (`android/v*` tags), Gradle-native signing with base64 keystore Secret

## Метрики

| Метрика | Значение |
|---------|----------|
| Backend тестов | 620 |
| Frontend тестов | 375 |
| Покрытие | ~80% |
| API endpoints | ~75 |
| Моделей | 19 |
| Миграций | 22 |
| Frontend страниц | 13 |
| Линтеры | Ruff + ESLint clean |
| Build | TypeScript + Vite clean |
| Android APK | ~3.8 MB (debug) |
