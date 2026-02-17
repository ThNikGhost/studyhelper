# Статус проекта StudyHelper

## Общий прогресс
- **Фаза**: Production
- **Прогресс**: MVP 100%. Все post-MVP фичи реализованы. Production с SSL на https://studyhelper1.ru.
- **Дата обновления**: 2026-02-17 (release signing)

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

React.lazy() code splitting, PWA (offline fallback, update prompt), dark theme (system/light/dark).

## Деплой
- **URL**: https://studyhelper1.ru (89.110.93.63)
- **SSL**: Let's Encrypt, certbot auto-renewal (12h)
- **Контейнеры**: db, redis, backend, nginx, certbot (5 шт.)
- **Миграции**: 22 применено
- **Sync**: APScheduler каждые 6ч + Redis distributed lock
- **Backups**: pg_dump daily cron (3:00 UTC), gzip, 7-day rotation

## Что в работе

Все B1-B12 bugfixes и F1-F5 post-MVP фичи завершены и задеплоены.

### Завершено (закоммичено):
- **B1-B3**: ClassmatesPage mobile fixes (grid, аватарки, кнопка "+")
- **B4**: Schedule scroll indicator — fade-градиент справа на мобильных
- **B5**: SettingsPage padding fix
- **B6**: ThemeToggle → Settings (перенос, удаление мёртвых файлов, aria-pressed)
- **B7**: Remove "Notes" tab (route + QuickActions)
- **B8**: GradesPage light theme contrast — border-классы к grade badges
- **B9**: Semester dates from LK — _determine_current_semester(), auto-dates, is_current fix
- **B11**: File download JWT fix — blob download с авторизацией
- **B12**: Nginx healthcheck path — `http://localhost/health` вместо `https://localhost/`
- **F1**: PostgreSQL backups — pg_dump cron daily, gzip, 7-day rotation, restore script
- **F2**: Sentry integration — sentry-sdk[fastapi] + @sentry/react, conditional init, user context
- **F3**: Telegram bot — aiogram 3.25, webhook mode, 9 команд + reply-keyboard, 5 типов уведомлений, SettingsPage integration
- **F3.1**: Telegram bot simplification — убраны /week /grades /attendance, добавлена ReplyKeyboardMarkup (📚 Расписание на сегодня, ⏭ Следующее занятие)
- **F4**: iCalendar (.ics) feed — подписка на расписание + дедлайны, icalendar 7.x, per-user token auth, SettingsPage UI, 27 тестов
- **F5**: Phone Widgets — API ключ + JSON endpoint для виджетов, shared filter refactor, Scriptable JS, SettingsPage UI с инструкциями, 29 тестов
- **F5.1**: Widget /today endpoint — полное расписание на день + первая будущая пара, offline кеш с локальным minutes_until, 24h cache TTL, shared auth refactor, текстовые фиксы виджета, 14 новых тестов
- **F5.2**: Android Widget App — нативный APK (4×2 виджет), AGP 9.0.0 + built-in Kotlin, RemoteViews, WorkManager 30min refresh, SharedPreferences cache, GitHub Actions CI → GitHub Releases
- **F5.3**: Android Chronometer + unified location — real-time countdown (system Chronometer вместо static text), парсер/бэкенд/фронтенд нормализация "Корпус"/"корп." в location, timeline building field
- **B13**: Fix "ауд." location parsing — `_parse_audit_corps` обрабатывает `"ауд. 114) Спортивный зал, 6("` → `("6", "114")`, defense-in-depth в `_clean_room` и frontend `formatLocation`
- **SEC-1**: Security Audit Phase 1+2 — rate limit /refresh, Telegram strict secret, file ownership check, VK URL sanitization, mass-assignment fix, Permissions-Policy, server_tokens off, CI permissions + SHA-pinning, /metrics IP check, passlib removal, LkSyncError generic messages, backup encryption, Docker pinning, dev-compose hardening
- **Cleanup**: Removed dead Celery module (backend/src/tasks/, 160 lines), celery optional dep, .gitignore Celery section, completed plan files
- **SEC-1.1**: Code review fixes — /metrics constants+fallback, REDISCLI_AUTH healthcheck, GPG passphrase-fd, allowed_fields comment, .env.example update, docker-compose comment
- **F6**: Release Signing — conditional release/debug build в CI, keystore через base64 GitHub Secret, Gradle-native signing, version bump 1.3.0, UpdateChecker → app-release.apk

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
- **Telegram**: aiogram 3.25 webhook mode, conditional init (token-gated), 9 commands + reply keyboard, CronTrigger notifications
- **Calendar Feed**: icalendar 7.x, per-user token URL auth, schedule + deadline events, subgroup/PE filtering, REFRESH-INTERVAL 6h
- **Widget API**: per-user token query param auth, next lesson + today schedule JSON endpoints, 7-day lookahead, subgroup/PE filtering, Scriptable JS widget with offline cache
- **Observability**: structlog (JSON prod / ConsoleRenderer dev), X-Request-ID, Prometheus metrics (/metrics), Sentry error tracking (optional, DSN-gated)
- **CI**: GitHub Actions (backend lint+test, frontend lint+build, Android conditional release/debug build on tag)
- **Android Widget**: Native APK (AGP 9.0.0, Kotlin built-in, Gradle 9.3.1), 4×2 AppWidgetProvider + RemoteViews, system Chronometer real-time countdown, WorkManager 30min refresh, HttpURLConnection + org.json (no external deps), SharedPreferences (API key + 24h JSON cache), release-signed APK via GitHub Releases (`android/v*` tags), Gradle-native signing with base64 keystore Secret

## Метрики

| Метрика | Значение |
|---------|----------|
| Backend тестов | 619 |
| Frontend тестов | 375 |
| Покрытие | ~80% |
| API endpoints | ~75 |
| Моделей | 19 |
| Миграций | 22 |
| Frontend страниц | 13 |
| Линтеры | Ruff + ESLint clean |
| Build | TypeScript + Vite clean |
| Android APK | ~3.8 MB (debug) |
