# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит (2026-03-02): feat(files): add work file attachments with review fixes (216c1b2).

## Следующие шаги (по приоритету)
- Задеплоить 216c1b2 на prod:
  ```
  git pull && docker compose -f docker-compose.prod.yml up -d --build backend frontend
  ```
  (нужна миграция: `docker compose -f docker-compose.prod.yml exec backend uv run alembic upgrade head`)
- (Фаза 3) httpOnly cookies — access token в памяти, refresh в httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет

## Известные pre-existing падения тестов
- `SchedulePage.test.tsx` — 3 теста падают (hidden subjects filter применяется в mock-данных)
- Не связаны с текущими изменениями, существуют с момента добавления фильтрации расписания
