# Проект: StudyHelper

## Память проекта (автозагрузка)
@docs/project_status.md
@docs/Current_task.md

## Описание
**StudyHelper** — персональное PWA для студентов ОмГУ: расписание (автопарсинг), дедлайны, файлы, инфо о преподавателях и группе.

## Стек
| Слой | Технологии |
|------|-----------|
| Frontend | React 19 + TypeScript + Vite, Tailwind v4 + shadcn/ui, Zustand, TanStack Query |
| Backend | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 async |
| БД / Кеш | PostgreSQL + asyncpg, Alembic, Redis |
| Парсинг | httpx + SHA-256 (HTTP API OmSU) |
| Инфра | Docker Compose, GitHub Actions CI |

## Критические правила
- **NEVER** хардкодь секреты — только env vars
- **NEVER** используй `git add -A` — добавляй конкретные файлы
- **MUST** проверять тесты и линтер перед коммитом
- **MUST** использовать conventional commits: `type(scope): description`
- **MUST** писать type hints (Python) и strict TypeScript
- Комментарии и код на **английском**, общение на **русском**
- Все пользователи видят общие данные (расписание, предметы, работы), WorkStatus/Notes/Attendance per user

## Команды
| Действие | Backend | Frontend |
|----------|---------|----------|
| Зависимости | `cd backend && uv sync` | `cd frontend && npm install` |
| Dev-сервер | `cd backend && uv run uvicorn src.main:app --reload` | `cd frontend && npm run dev` |
| Тесты | `cd backend && uv run pytest` | `cd frontend && npm run test` |
| Линтинг | `cd backend && uv run ruff check . && uv run ruff format .` | `cd frontend && npm run lint` |
| Миграции | `cd backend && uv run alembic upgrade head` | — |

## Ключевые файлы
- `docs/StudyHelper_TZ.md` — техническое задание
- `docs/Decisions.md` — архитектурные решения
- `docs/database_schema.md` — схема БД
- `docs/plans/tasks/` — активные задачи (B1-B12, F1-F5)

## Workflow сессии
- `/session-start` — загрузить контекст проекта
- `/session-end` — сохранить прогресс
- `/commit` — проверить тесты/линтер и запушить
- `/test` — запустить тесты с отчётом
