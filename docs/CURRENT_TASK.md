# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит (2026-02-21): fix: address all code review issues (19 fixes across backend/frontend/android).

### Что сделано в этой сессии (2026-02-21):
- Деплой миграции `k1l2m3n4o5p6` на прод — миграция оказалась уже применена
- Подтверждён статус продакшна: все 5 контейнеров healthy, 27/27 миграций применено

## Следующие шаги (по приоритету)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
