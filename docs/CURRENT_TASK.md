# Текущая задача

## Статус
**F3 Telegram bot реализован. Требует деплоя (Telegram Bot Token от @BotFather). Следующая: F5 (Phone widgets).**

## Последняя сессия: F3 Telegram Bot — 2026-02-15

### Сделано
- **F3 foundation**: TelegramLink model, schemas, service layer, alembic migration
- **F3 bot core**: aiogram 3.25, webhook mode, 15 команд бота (start/link/unlink/status, today/tomorrow/week/next, deadlines/grades/attendance, notifications/notify/morning)
- **F3 formatters**: Форматирование расписания, дедлайнов, оценок, посещаемости для Telegram
- **F3 notifications**: 5 типов — утренняя сводка (7:30), дедлайн-алерты (8:00/20:00), изменение расписания (hook), inline keyboard toggles
- **F3 frontend**: Telegram card в SettingsPage (3 состояния: не привязан → код → привязан), notification toggles, countdown timer
- **F3 infra**: docker-compose.prod.yml +3 env vars, conditional init (token-gated)
- **Gotcha**: Webhook secret validation через `X-Telegram-Bot-Api-Secret-Token` header (FastAPI, не aiohttp SimpleRequestHandler)

### Архитектура
- Модуль `backend/src/telegram/` — bot.py, formatters.py, keyboards.py, notifications.py, jobs.py, handlers/
- Webhook endpoint: `POST /api/v1/telegram/webhook` (secret header validation)
- REST API: status, link-code, unlink, notifications (JWT-protected)
- APScheduler CronTrigger jobs для утренней сводки и дедлайн-проверок
- Schedule change hook в `_sync_schedule_with_lock()` при `changed=True`

## Следующие шаги (по приоритету)
1. **F3 deploy** — Получить Bot Token от @BotFather, добавить env vars на сервер, миграция, деплой
2. **F5** — Phone widgets
3. **F4** — Google Calendar sync

## Блокеры / Вопросы
- F3 deploy требует Telegram Bot Token от @BotFather
- F4 требует Google Cloud Console проект
