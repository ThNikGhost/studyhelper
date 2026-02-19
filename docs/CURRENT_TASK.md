# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован, протестирован и работает в проде.**

Последний коммит `fc4298c` (2026-02-19): feat(works) — fix timezone bug, optional deadline time, batch add.

### Что сделано сегодня (2026-02-19):
- feat(works): улучшение дедлайнов в разделе «Работы»:
  - Fix timezone bug: appendTimezoneOffset + toLocalDatetimeString (off-by-one day)
  - deadline_has_time: миграция, модель, схемы, сервис, ICS (all-day events), Telegram (3 места)
  - Split date/time форма: отдельные поля даты и времени, время необязательно
  - Batch mode: добавление нескольких работ за раз (общие предмет/тип, разные названия/даты)
  - formatDeadline обновлён: показывает время когда hasTime=true
  - Обновлены тесты dateUtils + DeadlinesWidget
- feat: hidden subjects — per-user настройка скрытия предметов (не закоммичено)
- fix: Redis distributed lock, schedule hash fix, Android widget countdown fix

### Не закоммичено:
- Hidden subjects feature (13 файлов + миграция + тесты) — ожидает отдельный коммит

## Следующие шаги (по приоритету)
- Закоммитить hidden subjects feature
- Деплой всех изменений на прод (миграции b2c3d4e5f6g8 + a1b2c3d4e5f7)
- Сборка и тестирование Android APK с fix countdown (тег `android/v*` для release)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
