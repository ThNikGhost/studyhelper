# Статус проекта StudyHelper

## Последнее обновление
- **Дата**: 2026-02-07
- **Сессия**: Реализация 04-dashboard-widget (улучшение виджетов Dashboard)

## Общий прогресс
**Фаза**: Post-MVP реализация
**Прогресс**: MVP 100% завершён. 01-PWA реализована. 04-dashboard-widget реализован.

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
- [x] Alembic миграции (9 миграций применено)

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

---

## Что в работе

Нет активных задач. 04-dashboard-widget реализован, ожидает коммит.

### Следующие задачи (приоритет):
1. ~~**01-PWA** — manifest, service worker, оффлайн (P0)~~ ✅
2. ~~**04-dashboard-widget** — виджеты Dashboard (P1)~~ ✅
3. **06-clickable-schedule** — кликабельные элементы расписания (P1)
4. **09-dark-theme** — тёмная тема (P2)
5. **07-progress-bars** — прогресс-бары по предметам (P2)
6. **03-file-upload-ui** — UI загрузки файлов (P1)
7. **05-ics-export** — экспорт в .ics (P2)
8. **02-push-notifications** — push-уведомления (P1, зависит от PWA ✅)
9. **08-attendance** — посещаемость (P2)
10. **10-lesson-notes** — заметки к парам (P2)
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

---

## Метрики

| Метрика | Значение |
|---------|----------|
| Тестов backend | 264 |
| Тестов frontend | 114 |
| Покрытие тестами | ~80% |
| API endpoints | ~55 |
| Моделей | 13 |
| Миграций | 9 |
| Линтер backend | ✅ Ruff проходит |
| Линтер frontend | ✅ ESLint проходит (кроме shadcn/ui) |
| Frontend тесты | ✅ Vitest проходит (114 тестов) |
| Frontend build | ✅ TypeScript + Vite |
| Frontend страниц | 8 (Login, Register, Dashboard, Schedule, Subjects, Works, Semesters, Classmates) |
