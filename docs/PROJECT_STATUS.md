# Статус проекта StudyHelper

## Последнее обновление
- **Дата**: 2026-02-03
- **Сессия**: Backend MVP завершён

## Общий прогресс
**Фаза**: MVP разработка
**Прогресс**: ~50% (backend готов, frontend не начат)

---

## Что сделано

### Документация
- [x] Техническое задание (docs/StudyHelper_TZ.md)
- [x] CLAUDE.md — обновлён под проект
- [x] plans/MVP_plan.md — план MVP
- [x] plans/backend_plan.md — план backend разработки
- [x] plans/future_features.md — планы на будущее

### Инфраструктура
- [x] Docker Compose (PostgreSQL 16, Redis 7, Adminer)
- [x] .env.example — переменные окружения
- [x] GitHub repository

### Backend (ЗАВЕРШЁН)
- [x] Инициализация проекта (pyproject.toml, uv)
- [x] Конфигурация (pydantic-settings)
- [x] База данных (SQLAlchemy 2.0 async)
- [x] Alembic миграции (7 миграций применено)

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
| Schedule | ✅ ScheduleEntry, ScheduleSnapshot | ✅ | ✅ | ✅ | ✅ 26 |

#### API Endpoints:
- `/api/v1/auth/*` — аутентификация (register, login, refresh, logout, me)
- `/api/v1/semesters/*` — семестры (CRUD + set-current)
- `/api/v1/subjects/*` — предметы (CRUD + works by subject)
- `/api/v1/works/*` — работы (CRUD + status, history, upcoming)
- `/api/v1/teachers/*` — преподаватели (CRUD)
- `/api/v1/university/departments/*` — кафедры (CRUD)
- `/api/v1/university/buildings/*` — корпуса (CRUD)
- `/api/v1/classmates/*` — одногруппники (CRUD)
- `/api/v1/schedule/*` — расписание (week, today, current, entries CRUD, snapshots)

---

## Что в работе

### Следующая задача: Frontend
- [ ] Инициализация Vite + React + TypeScript
- [ ] Настройка Tailwind CSS + shadcn/ui
- [ ] Страницы: Login, Register
- [ ] Защищённые роуты
- [ ] Dashboard

---

## Что отложено (на будущее)

### Backend (Etap 10)
- [ ] Celery для фоновых задач
- [ ] Playwright парсер расписания ОмГУ
- [ ] Push-уведомления (pywebpush)

### Фаза 2
- Push-уведомления
- Файловое хранилище
- Посещаемость
- Календарь
- Прогресс-бары
- Учебный план

---

## Известные проблемы

### Windows + PostgreSQL драйверы
На Windows есть проблемы с кодировкой при подключении Python драйверов к PostgreSQL.

**Решение**: Запускать миграции через `docker exec`:
```bash
docker compose exec db psql -U studyhelper -d studyhelper -c "SQL_QUERY"
```

---

## Архитектурные заметки

- **Парный режим**: два пользователя видят все данные, WorkStatus создаётся для каждого
- **История статусов**: WorkStatusHistory автоматически при изменении статуса
- **Аутентификация**: JWT (access 15min, refresh 7days), макс 2 пользователя
- **База данных**: PostgreSQL + aiosqlite для тестов
- **Расписание**: поддержка чётных/нечётных недель (week_type)

---

## Метрики

| Метрика | Значение |
|---------|----------|
| Тестов | 170 |
| Покрытие тестами | 79% |
| API endpoints | ~50 |
| Моделей | 13 |
| Миграций | 7 |
| Линтер | ✅ Ruff проходит |
