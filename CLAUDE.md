# Проект: StudyHelper

## Память проекта (автозагрузка)
@docs/project_status.md
@docs/Current_task.md

## Описание
**StudyHelper** — персональное PWA-приложение для студентов ОмГУ им. Ф.М. Достоевского: расписание (автопарсинг), дедлайны, файлы, инфо о преподавателях и группе. Поддерживает парный режим для двух пользователей.

## Стек технологий
- **Frontend**: React + TypeScript + Vite, Tailwind CSS + shadcn/ui, Zustand
- **Backend**: Python 3.12+, FastAPI, Pydantic v2
- **БД**: PostgreSQL, SQLAlchemy 2.0 + asyncpg, Alembic
- **Фоновые задачи**: Celery + Redis
- **Парсинг**: Playwright
- **Push**: Web Push API + pywebpush
- **Контейнеризация**: Docker + Docker Compose

## Структура проекта
```
/
├── frontend/            # PWA Frontend (React + Vite)
├── backend/             # Python Backend (FastAPI)
├── docker/              # Docker конфигурация
├── docs/                # Документация
│   ├── plans/           # Планы разработки
│   ├── API.md           # Документация API
│   ├── database_schema.md
│   ├── deployment.md
│   ├── Current_task.md
│   ├── Decisions.md
│   └── project_status.md
└── .github/workflows/   # CI/CD пайплайны
```

## Команды

### Backend
```bash
cd backend
uv sync                              # Установка зависимостей
uv run uvicorn src.main:app --reload # Dev-сервер
uv run pytest                        # Тесты
uv run ruff check . && uv run ruff format .  # Линтинг
uv run alembic upgrade head          # Миграции
```

### Frontend
```bash
cd frontend
npm install              # Установка зависимостей
npm run dev              # Dev-сервер
npm run build            # Сборка
npm run test             # Тесты
npm run lint             # Линтинг
```

### Docker
```bash
docker-compose up -d --build         # Запуск всех сервисов
docker-compose -f docker-compose.prod.yml up -d  # Продакшн
docker-compose logs -f               # Логи
```

## Соглашения

### Python
- Форматирование: Ruff
- Линтинг: Ruff
- Type hints обязательны
- Docstrings в формате Google

### TypeScript
- Форматирование: Prettier
- Линтинг: ESLint
- Строгий режим TypeScript

### Тестирование
- Backend: pytest (минимум 80% покрытия)
- Frontend: Vitest + React Testing Library

## Сервер (облако)
- **Адрес**: [IP или домен — уточнить]
- **SSH пользователь**: [user]
- **Путь к проекту**: /home/[user]/studyhelper
- **Сервис**: Docker Compose

### Проверка статуса
```bash
docker-compose ps
docker-compose logs -f backend
sudo systemctl status postgresql
```

## Важные файлы
- `backend/pyproject.toml` — конфигурация backend
- `frontend/package.json` — конфигурация frontend
- `docker-compose.yml` — локальная разработка
- `docker-compose.prod.yml` — продакшн
- `.env` — переменные окружения (НЕ КОММИТИТЬ!)
- `docs/StudyHelper_TZ.md` — техническое задание

## Ключевые ссылки
- **ТЗ проекта**: `docs/StudyHelper_TZ.md`
- **План MVP**: `docs/plans/MVP_plan.md`
- **Полный план**: `docs/plans/full_plan.md`
- **Архитектурные решения**: `docs/Decisions.md`
- **Схема БД**: `docs/database_schema.md`

## Текущие задачи
См. `docs/project_status.md` и `docs/Current_task.md`

## Принятые решения
См. `docs/Decisions.md`

## Команды сессии
- `/session-start` — начать сессию (прочитать контекст)
- `/session-end` — завершить сессию (сохранить контекст)
- `/commit` — коммит и пуш на GitHub

## Правило: Коммиты
После завершения важной фичи, исправления бага или логического блока работы:
1. Проверь тесты: `uv run pytest -q` / `npm run test`
2. Проверь линтер: `uv run ruff check .` / `npm run lint`
3. Сделай коммит и пуш: `/commit`

Не накапливай много изменений — коммить часто и атомарно.
