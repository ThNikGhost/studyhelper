# Статус проекта StudyHelper

## Общий прогресс
- **Фаза**: Production
- **Прогресс**: MVP 100%. Все post-MVP фичи реализованы. Production с SSL на https://studyhelper1.ru.
- **Дата обновления**: 2026-02-15

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
| Parser | +subgroup parsing | — | — | CLI | 82 |
| Uploads | — | — | — | — | 11 |
| Files | File | — | — | — | 21 |
| Attendance | Absence | +total_planned/completed | semester filter | — | 29 |
| Notes | LessonNote | — | upsert | — | 26 |
| LK | LkCredentials, SessionGrade, SemesterDiscipline | +LkImportResult | +import_to_app | +/import | 51 |

## Frontend

13 страниц: Login, Register, Dashboard, Schedule, Subjects, Works, Semesters, Classmates, Files, Attendance, Timeline, Settings, Grades. (Notes убрана из навигации, доступна через LessonDetailModal)

React.lazy() code splitting, PWA (offline fallback, update prompt), dark theme (system/light/dark).

## Деплой
- **URL**: https://studyhelper1.ru (89.110.93.63)
- **SSL**: Let's Encrypt, certbot auto-renewal (12h)
- **Контейнеры**: db, redis, backend, nginx, certbot (5 шт.)
- **Миграции**: 19 применено
- **Sync**: APScheduler каждые 6ч + Redis distributed lock

## Что в работе

См. `docs/Current_task.md` — все B1-B12 bugfixes завершены, осталось F1-F5 features.

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

### Следующие задачи (приоритет):
1. **F1** — PostgreSQL backups
2. **F2** — Sentry integration

## Что отложено
- httpOnly cookies вместо localStorage
- Механизм отзыва JWT

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
- **Observability**: structlog (JSON prod / ConsoleRenderer dev), X-Request-ID, Prometheus metrics (/metrics)
- **CI**: GitHub Actions (backend lint+test, frontend lint+build)

## Метрики

| Метрика | Значение |
|---------|----------|
| Backend тестов | 471 |
| Frontend тестов | 375 |
| Покрытие | ~80% |
| API endpoints | ~70 |
| Моделей | 16 |
| Миграций | 19 |
| Frontend страниц | 13 |
| Линтеры | Ruff + ESLint clean |
| Build | TypeScript + Vite clean |
