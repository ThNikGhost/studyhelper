# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит `5791122` (2026-02-19): fix(migration) — correct alembic down_revision to latest head.

### Что сделано в этой сессии (2026-02-19):
- feat(hidden-subjects): per-lesson-type subject hiding
  - Backend: hidden_subjects изменён с `list[int]` на `dict[str, list[str] | null]`
  - Backend: per-type фильтрация в schedule_filters (calendar, widget)
  - Backend: data migration h8i9j0k1l2m3 (list→dict конвертация)
  - Frontend: UI с цветными чипами типов занятий в SettingsPage
  - Frontend: двухуровневая фильтрация (per-type для расписания, fully-hidden для остальных)
  - Frontend: обновлены все 5 consuming pages + localStorage migration
  - 21 файл изменён, 11 новых тестов (642 backend, 388 frontend)
- fix(migration): исправлен down_revision (multiple heads → single head)
- Успешный деплой на прод, все контейнеры healthy

## Следующие шаги (по приоритету)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
