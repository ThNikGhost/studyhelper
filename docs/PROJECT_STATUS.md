# Статус проекта StudyHelper

## Последнее обновление
- **Дата**: 2026-02-07
- **Сессия**: Frontend тесты — инфраструктура + 70 тестов

## Общий прогресс
**Фаза**: MVP разработка
**Прогресс**: 100% (backend + frontend + code review + frontend тесты завершены)

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
- [x] Тесты утилит: dateUtils (15), errorUtils (13), constants (6)
- [x] Тесты store: authStore (11)
- [x] Тесты компонентов: ProtectedRoute (3), ErrorBoundary (3), Modal (6)
- [x] Тесты страниц: LoginPage (6), DashboardPage (10)
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

---

## Что в работе

Нет активных задач.

### Следующие задачи:
1. Деплой MVP на сервер
2. PWA настройка (service worker, manifest)

---

## Что отложено (на будущее)

### Отдельный PR (из Code Review)
- httpOnly cookies вместо localStorage
- Механизм отзыва JWT
- Docker production config

### Фаза 2
- Push-уведомления
- Файловое хранилище
- Посещаемость
- Календарь
- Прогресс-бары
- Учебный план
- Кликабельные элементы расписания

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
**Решение**: Использовать `pool: 'forks'` в конфиге + `timeout` при запуске из CI. Все 70 тестов проходят корректно, подвисание только при cleanup.

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

---

## Метрики

| Метрика | Значение |
|---------|----------|
| Тестов backend | 264 |
| Тестов frontend | 70 |
| Покрытие тестами | ~80% |
| API endpoints | ~55 |
| Моделей | 13 |
| Миграций | 9 |
| Линтер backend | ✅ Ruff проходит |
| Линтер frontend | ✅ ESLint проходит (кроме shadcn/ui) |
| Frontend тесты | ✅ Vitest проходит (70 тестов) |
| Frontend build | ✅ TypeScript + Vite |
| Frontend страниц | 8 (Login, Register, Dashboard, Schedule, Subjects, Works, Semesters, Classmates) |
