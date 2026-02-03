# Статус проекта StudyHelper

## Последнее обновление
- **Дата**: 2026-02-03
- **Сессия**: Инициализация backend

## Общий прогресс
**Фаза**: MVP разработка
**Прогресс**: ~15% (backend инициализирован, auth готов)

---

## Что сделано

### Документация
- [x] Техническое задание (docs/StudyHelper_TZ.md)
- [x] CLAUDE.md — обновлён под проект
- [x] Current_task.md — текущая задача
- [x] Decisions.md — архитектурные решения
- [x] project_status.md — статус проекта
- [x] plans/MVP_plan.md — план MVP
- [x] plans/full_plan.md — полный план разработки
- [x] plans/future_features.md — планы на будущее
- [x] plans/backend_plan.md — план backend разработки

### Инфраструктура
- [x] Docker Compose (PostgreSQL 16, Redis 7, Adminer)
- [x] .env.example — переменные окружения

### Backend
- [x] Инициализация проекта (pyproject.toml, uv)
- [x] Конфигурация (pydantic-settings)
- [x] База данных (SQLAlchemy 2.0 async)
- [x] Alembic миграции (первая миграция применена)
- [x] Модель User с TimestampMixin
- [x] JWT аутентификация (access + refresh tokens)
- [x] Auth API endpoints:
  - POST /api/v1/auth/register
  - POST /api/v1/auth/login
  - POST /api/v1/auth/refresh
  - GET /api/v1/auth/me
  - POST /api/v1/auth/logout
- [x] Health endpoints (/, /health)
- [x] Базовые тесты (2 passing)

---

## Что в работе

### Текущая задача: Продолжение backend
- [ ] Написать тесты для auth endpoints
- [ ] Модели семестров и предметов
- [ ] CRUD для семестров/предметов
- [ ] Модель работ (deadlines)

---

## Что запланировано

### MVP (Фаза 1)
1. ~~Аутентификация (2 пользователя)~~ ✅
2. Расписание (парсинг + отображение)
3. Предметы (CRUD)
4. Работы (CRUD + статусы + дедлайны)
5. Преподаватели (CRUD)
6. Инфо об универе (CRUD)
7. Одногруппники (CRUD)
8. Dashboard
9. PWA (manifest + service worker)
10. Адаптив + тёмная тема
11. Парный режим (просмотр)

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
На Windows есть проблемы с кодировкой при подключении Python драйверов к PostgreSQL:
- psycopg2 и psycopg3 не могут декодировать русские сообщения от сервера
- asyncpg имеет проблемы с asyncio на Windows

**Решение**: Запускать миграции через `docker exec`:
```bash
docker exec studyhelper-db psql -U studyhelper -d studyhelper -c "SQL_QUERY"
```

---

## Блокеры и риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Изменение структуры сайта расписания | Средняя | Высокое | Мониторинг, гибкий парсер |
| Сложность PWA на iOS | Низкая | Среднее | Тестирование на реальных устройствах |
| Windows + Postgres drivers | — | — | Использовать docker exec для миграций |

---

## Архитектурные заметки

- **Парный режим**: два пользователя видят все данные, редактируют только своё (статусы, посещаемость)
- **Парсинг**: Playwright + Celery, хеширование для определения изменений
- **Аутентификация**: JWT (access 15min, refresh 7days)
- **База данных**: PostgreSQL + asyncpg для async, psycopg для миграций

---

## Метрики

| Метрика | Значение |
|---------|----------|
| Файлов Python (backend) | ~15 |
| Покрытие тестами | ~10% |
| API endpoints реализовано | 5 / ~50 |
| Моделей | 1 / 10 |
| Миграций | 1 |
