# Текущая задача

## Статус
**F1 завершена. Следующая: F2 (Sentry integration).**

## Последняя сессия: F1 PostgreSQL backups — 2026-02-15

### Сделано
- **F1**: PostgreSQL автобэкапы на продакшене
- `scripts/backup.sh` — pg_dump через Docker, gzip, ротация 7 дней, логирование
- `scripts/restore.sh` — интерактивное восстановление из .sql.gz
- Cron: ежедневно в 3:00 UTC → `/var/log/studyhelper-backup.log`
- Тестовый бэкап: 296K, валидный SQL дамп
- Все коммиты запушены на origin

## Следующие шаги (по приоритету)
1. **F2** — Sentry integration
2. **F5** — Phone widgets
3. **F3** — Telegram bot
4. **F4** — Google Calendar sync

## Блокеры / Вопросы
- F2 требует создание аккаунта Sentry
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
