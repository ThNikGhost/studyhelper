# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован, протестирован и работает в проде.**

Последний коммит `aa862fe` (2026-02-19): fix(android) — countdown больше не уходит в минус при начале пары (precise timing + AlarmManager refresh).

### Что сделано сегодня (2026-02-19):
- fix: Redis distributed lock для morning summary и deadline alert jobs (предотвращает дубликаты при `--workers 2`)
- fix: исключение volatile поля `lesson_date` из `compute_schedule_hash()` — хеш стабилен при еженедельной смене дат
- fix(android): countdown виджета больше не тикает в минус:
  - `computePreciseMsUntil()` — точность до секунды вместо минут
  - `scheduleUpdateAlarm()` — AlarmManager exact alarm на момент начала пары
  - `WidgetRefreshReceiver` — BroadcastReceiver для обновления виджета при срабатывании alarm
  - Cleanup alarm в `onDisabled()`

## Следующие шаги (по приоритету)
- Деплой backend-фиксов на прод (Redis lock + hash fix) и проверка логов
- Сборка и тестирование Android APK с fix countdown (тег `android/v*` для release)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
