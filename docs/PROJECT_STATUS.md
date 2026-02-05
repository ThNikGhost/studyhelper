# Статус проекта StudyHelper

## Последнее обновление
- **Дата**: 2026-02-05
- **Сессия**: ClassmatesPage завершена, MVP frontend готов

## Общий прогресс
**Фаза**: MVP разработка
**Прогресс**: ~95% (backend готов + парсер + все frontend страницы)

---

## Что сделано

### Документация
- [x] Техническое задание (docs/StudyHelper_TZ.md)
- [x] CLAUDE.md — обновлён под проект
- [x] plans/MVP_plan.md — план MVP
- [x] plans/backend_plan.md — план backend разработки
- [x] plans/future_features.md — планы на будущее (обновлено)
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
| Uploads | — | ✅ | — | ✅ | ✅ 11 |

### Parser модуль (ЗАВЕРШЁН ✅)
- [x] `src/parser/` — модуль парсинга
- [x] `src/cli/schedule_cli.py` — CLI команды (parse, sync)
- [x] `src/tasks/schedule_tasks.py` — Celery задачи (подготовлены)
- [x] `POST /api/v1/schedule/refresh` — API endpoint для синхронизации
- [x] Протестировано на реальном API: **3088 записей**

### Frontend (ПОЧТИ ЗАВЕРШЁН)
- [x] Инициализация Vite + React 19 + TypeScript
- [x] Tailwind CSS v4 настроен
- [x] UI компоненты (Button, Input, Card, Label, Calendar, Popover)
- [x] API клиент (axios с interceptors для JWT)
- [x] Auth store (Zustand)
- [x] Роутинг (react-router-dom)
- [x] Защищённые маршруты (ProtectedRoute)
- [x] Страницы: LoginPage, RegisterPage, DashboardPage
- [x] SchedulePage ✅ (кастомный календарь, локальное время)
- [x] SubjectsPage ✅
- [x] WorksPage ✅
- [x] SemestersPage ✅ (CRUD для семестров)
- [x] ClassmatesPage ✅ (CRUD, контакты)

---

## Что в работе

### Текущая задача: Dashboard виджеты (ЗАВЕРШЕНО ✅)
Добавлены виджеты на главную страницу:
- [x] Виджет текущего/следующего занятия
- [x] Виджет ближайших дедлайнов
- [ ] Виджет статистики — опционально

### Выполнено в этой сессии:
- [x] ClassmatesPage — страница одногруппников (CRUD, группировка по подгруппам)
- [x] Uploads модуль — загрузка/удаление аватарок
- [x] Аватарки отображаются на карточках одногруппников

### Следующие задачи:
1. Dashboard виджеты
2. Тестирование всех страниц
3. Деплой MVP

---

## Что отложено (на будущее)

### Фаза 2
- Push-уведомления
- Файловое хранилище
- Посещаемость
- Календарь
- Прогресс-бары
- Учебный план
- Кликабельные элементы расписания (предмет → страница предмета)

---

## Известные проблемы

### Windows + Docker + asyncpg
На Windows есть критические проблемы с asyncpg при подключении к PostgreSQL в Docker.
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
- **Расписание**: lesson_date для конкретных дат занятий
- **Парсер**: HTTP API (httpx) + SHA-256 хеширование для отслеживания изменений
- **API расписания**: `https://eservice.omsu.ru/schedule/backend/schedule/group/{group_id}`
- **Frontend**: Vite + React 19 + TypeScript + Tailwind v4 + Zustand + React Query
- **Календарь**: react-day-picker v9 + @radix-ui/react-popover

---

## Метрики

| Метрика | Значение |
|---------|----------|
| Тестов | 264 |
| Покрытие тестами | ~80% |
| API endpoints | ~55 |
| Моделей | 13 |
| Миграций | 8 |
| Линтер | ✅ Ruff проходит |
| Frontend страниц | 8 (Login, Register, Dashboard, Schedule, Subjects, Works, Semesters, Classmates) |
