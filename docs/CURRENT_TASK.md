# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит (2026-03-14): fix: full code review audit — 22 fixes (7850ab3).

## Следующие шаги (по приоритету)
- Задеплоить 7850ab3 на prod (включает CORS PATCH fix — критично):
  ```
  git pull && docker compose -f docker-compose.prod.yml up -d --build backend nginx
  ```
  (без новых миграций)
- (Фаза 3) httpOnly cookies — access token в памяти, refresh в httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет

## Известные pre-existing падения тестов
- `SchedulePage.test.tsx` — 3 теста падают (hidden subjects filter применяется в mock-данных)
- `test_telegram_schedule_utils.py::test_next_is_hidden` — flaky (time-dependent, hardcoded 23:00/23:30)
- Не связаны с текущими изменениями
