# Текущая задача

## Статус
**Нет активной задачи.** Production Docker config завершён.

## Последняя сессия: Production Docker Configuration

### Сделано
- [x] `backend/Dockerfile` — multi-stage build (python:3.12-slim + uv), non-root user, healthcheck via urllib
- [x] `backend/entrypoint.sh` — wait for PostgreSQL (socket check), alembic migrate, uvicorn с --proxy-headers
- [x] `backend/.dockerignore` — исключает .venv, tests, uploads, __pycache__, .env
- [x] `nginx/nginx.conf` — reverse proxy, rate limiting (30r/s API, 5r/m auth), gzip, security headers, PWA caching
- [x] `nginx/Dockerfile` — multi-stage (node:22-alpine build → nginx:1.27-alpine serve)
- [x] `docker-compose.prod.yml` — db (512MB), redis (192MB), backend (512MB), nginx (128MB), ~1.3GB total
- [x] `.env.production.example` — шаблон env для продакшена
- [x] `.dockerignore` (корень) — для nginx build context
- [x] `.gitignore` — добавлено `!.env.production.example`

### Незакоммичено
Все файлы созданы, но не закоммичены. Нужен коммит + пуш.

## Следующие задачи (приоритет)
1. **Деплой на сервер** — проверить Docker builds, деплой
2. **05-ics-export** — экспорт в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1, зависит от PWA)

## Блокеры / Вопросы
Нет блокеров.
