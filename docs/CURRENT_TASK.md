# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован, протестирован и работает в проде.**

Последний коммит `7fe5aad` (2026-02-19): fix — дубликаты Telegram-уведомлений (Redis lock для notification jobs) + ложные "Расписание обновлено" (исключение lesson_date из хеша).

### Что сделано сегодня (2026-02-19):
- fix: Redis distributed lock для morning summary и deadline alert jobs (предотвращает дубликаты при `--workers 2`)
- fix: исключение volatile поля `lesson_date` из `compute_schedule_hash()` — хеш стабилен при еженедельной смене дат
- test: `test_different_lesson_date_same_hash` — проверка стабильности хеша

## Следующие шаги (по приоритету)
- Деплой текущего коммита на прод и проверка логов (второй worker должен логировать "skipped: another worker holds the lock")
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
