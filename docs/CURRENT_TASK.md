# Текущая задача

## Статус
**F2 завершена и задеплоена на прод. Следующая: F5 (Phone widgets).**

## Последняя сессия: F2 Sentry Deploy — 2026-02-15

### Сделано
- **F2 base**: Sentry integration (backend + frontend)
- **F2 hardening** (6 улучшений): PII fix, CSP fix, EventScrubber, React 19 hooks, traces_sampler, Router v7 tracing
- **F2 deploy**: задеплоен на прод, тестовые события доставлены в Sentry dashboard
- **Gotcha**: DSN нужно добавлять в `.env` (не `.env.production`), т.к. Docker Compose читает `.env`

## Следующие шаги (по приоритету)
1. **F5** — Phone widgets
2. **F3** — Telegram bot
3. **F4** — Google Calendar sync

## Блокеры / Вопросы
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
