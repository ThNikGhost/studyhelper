# Текущая задача

## Статус
**B12 завершена. Следующая: F1 (PostgreSQL backups).**

## Последняя сессия: B12 Nginx healthcheck path — 2026-02-15

### Сделано
- **B12**: Healthcheck изменён с `https://localhost/` на `http://localhost/health`
- Убран SSL handshake — теперь проверяется реальный health endpoint (DB + Redis)
- 2 файла: `nginx/Dockerfile`, `docker-compose.prod.yml`
- `docker compose config` валиден

## Следующие шаги (по приоритету)
1. **F1** — PostgreSQL backups
2. **F2** — Sentry integration
4. **F5** — Phone widgets
5. **F3** — Telegram bot
6. **F4** — Google Calendar sync

## Блокеры / Вопросы
- F2 требует создание аккаунта Sentry
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
- 11 локальных коммитов не запушены на origin
