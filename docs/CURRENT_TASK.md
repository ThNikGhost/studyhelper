# Текущая задача

## Статус
**F2 hardening завершён. Следующая: F5 (Phone widgets).**

## Последняя сессия: F2 Sentry Hardening — 2026-02-15

### Сделано
- **F2 base**: Sentry integration (backend + frontend)
- **F2 hardening** (6 улучшений):
  1. PII fix — убран `username` (=email) из `Sentry.setUser()` (3 места в authStore.ts)
  2. CSP fix — добавлен `https://*.ingest.sentry.io` в `connect-src` (2 места в nginx.conf)
  3. EventScrubber — custom denylist (access_token, refresh_token, jwt, fernet_key, lk_password, credentials)
  4. React 19 error hooks — `onUncaughtError`/`onCaughtError` через `Sentry.reactErrorHandler` в createRoot()
  5. traces_sampler — drop /health + /metrics, 100% auth + schedule, 20% остальное (вместо flat 10%)
  6. React Router v7 tracing — `reactRouterV7BrowserTracingIntegration` + `SentryRoutes` wrapper

### Для активации на проде
1. Создать проекты на sentry.io (Python + React)
2. Добавить в `.env.production`:
   - `SENTRY_DSN=https://...@sentry.io/...` (backend)
   - `VITE_SENTRY_DSN=https://...@sentry.io/...` (frontend)
3. Пересобрать контейнеры: `docker compose -f docker-compose.prod.yml up -d --build`

## Следующие шаги (по приоритету)
1. **F5** — Phone widgets
2. **F3** — Telegram bot
3. **F4** — Google Calendar sync

## Блокеры / Вопросы
- F2 требует создание аккаунта Sentry + DSN
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
