# Статус проекта StudyHelper

## Последнее обновление
- **Дата**: 2026-02-04
- **Сессия**: Переписан парсер с Playwright на HTTP API

## Общий прогресс
**Фаза**: MVP разработка
**Прогресс**: ~80% (backend готов + парсер + SchedulePage)

---

## Что сделано

### Документация
- [x] Техническое задание (docs/StudyHelper_TZ.md)
- [x] CLAUDE.md — обновлён под проект
- [x] plans/MVP_plan.md — план MVP
- [x] plans/backend_plan.md — план backend разработки
- [x] plans/future_features.md — планы на будущее
- [x] plans/schedule_page_frontend_plan.md — план SchedulePage

### Инфраструктура
- [x] Docker Compose (PostgreSQL 16, Redis 7, Adminer) — для Linux/Mac
- [x] Локальный PostgreSQL — для Windows
- [x] .env.example — переменные окружения
- [x] GitHub repository

### Backend (ЗАВЕРШЁН)
- [x] Инициализация проекта (pyproject.toml, uv)
- [x] Конфигурация (pydantic-settings)
- [x] База данных (SQLAlchemy 2.0 async)
- [x] Alembic миграции (8 миграций применено)

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

### Parser модуль (ЗАВЕРШЁН ✅)
- [x] `src/parser/` — модуль парсинга
  - `exceptions.py` — кастомные исключения
  - `hash_utils.py` — хеширование для отслеживания изменений
  - `data_mapper.py` — маппинг данных на схемы
  - `omsu_parser.py` — HTTP API парсер (httpx)
- [x] `src/cli/schedule_cli.py` — CLI команды (parse, sync)
- [x] `src/tasks/schedule_tasks.py` — Celery задачи (подготовлены)
- [x] `POST /api/v1/schedule/refresh` — API endpoint для синхронизации
- [x] Протестировано на реальном API: **3088 записей**
- [x] 85 тестов парсера (74 parser + 11 sync)

### Frontend (В ПРОЦЕССЕ)
- [x] Инициализация Vite + React 18 + TypeScript
- [x] Tailwind CSS v4 настроен
- [x] UI компоненты (Button, Input, Card, Label)
- [x] API клиент (axios с interceptors для JWT)
- [x] Auth store (Zustand)
- [x] Роутинг (react-router-dom)
- [x] Защищённые маршруты (ProtectedRoute)
- [x] Страницы: LoginPage, RegisterPage, DashboardPage
- [x] Страница расписания (SchedulePage) ✅
- [ ] Страница предметов (SubjectsPage)
- [ ] Страница работ (WorksPage)
- [ ] Страница одногруппников (ClassmatesPage)

---

## Что в работе

### Завершено: SchedulePage ✅
- Парсер готов (3088 записей в БД)
- Frontend SchedulePage с навигацией по неделям

### Следующие задачи:
- SubjectsPage — страница предметов
- WorksPage — страница работ
- ClassmatesPage — страница одногруппников

---

## Что отложено (на будущее)

### Frontend страницы (после парсера)
- [ ] SchedulePage — план готов: `docs/plans/schedule_page_frontend_plan.md`
- [ ] SubjectsPage
- [ ] WorksPage
- [ ] ClassmatesPage

### Фаза 2
- Push-уведомления
- Файловое хранилище
- Посещаемость
- Календарь
- Прогресс-бары
- Учебный план

---

## Известные проблемы

### Windows + Docker + asyncpg
На Windows есть критические проблемы с asyncpg при подключении к PostgreSQL в Docker:
- ConnectionResetError из-за asyncio ProactorEventLoop
- Проблемы с кодировкой сообщений об ошибках (cp1251 vs UTF-8)

**Решение**: Использовать локальный PostgreSQL вместо Docker на Windows.

### Windows + Vite + localhost
Vite на Windows может не слушать на правильном адресе из-за IPv6/IPv4 резолвинга.

**Решение**: Явно указать `host: '127.0.0.1'` в vite.config.ts

---

## Архитектурные заметки

- **Парный режим**: два пользователя видят все данные, WorkStatus создаётся для каждого
- **История статусов**: WorkStatusHistory автоматически при изменении статуса
- **Аутентификация**: JWT (access 15min, refresh 7days), макс 2 пользователя
- **База данных**: PostgreSQL + aiosqlite для тестов
- **Расписание**: поддержка чётных/нечётных недель (week_type)
- **Парсер**: HTTP API (httpx) + SHA-256 хеширование для отслеживания изменений
- **API расписания**: `https://eservice.omsu.ru/schedule/backend/schedule/group/{group_id}`
- **Frontend**: Vite + React 18 + TypeScript + Tailwind v4 + Zustand

---

## Метрики

| Метрика | Значение |
|---------|----------|
| Тестов | 253 |
| Покрытие тестами | ~80% |
| API endpoints | ~55 |
| Моделей | 13 |
| Миграций | 8 |
| Линтер | ✅ Ruff проходит |
| Frontend страниц | 4 (Login, Register, Dashboard, Schedule) |
