# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован, протестирован и работает в проде.**

Последний коммит `7f0aa94` (2026-02-19): feat(settings) — hidden subjects per-user setting, скрытие предметов из всех представлений.

### Что сделано сегодня (2026-02-19):
- feat: hidden subjects — per-user настройка скрытия предметов:
  - Backend: миграция (JSON column), модель, схема с валидацией (max 100, dedup, positive-only), фильтрация в schedule_filters
  - Frontend: фильтрация на всех страницах (Schedule, Dashboard, Subjects, Works, Attendance)
  - Settings UI: карточка с toggle-кнопками предметов текущего семестра, очистка стейлых ID
  - 12 новых тестов (5 auth + 7 schedule_filters)
- fix: Redis distributed lock для morning summary и deadline alert jobs
- fix: исключение volatile поля `lesson_date` из `compute_schedule_hash()`
- fix(android): countdown виджета больше не тикает в минус

## Следующие шаги (по приоритету)
- Деплой hidden subjects + backend-фиксов на прод
- Сборка и тестирование Android APK с fix countdown (тег `android/v*` для release)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
