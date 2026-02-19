# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован, протестирован и работает в проде.**

Последний коммит `3f5a58f` (2026-02-19): docs — update status after hidden subjects feature.

### Что сделано сегодня (2026-02-19):
- feat(works): улучшение дедлайнов в разделе «Работы»:
  - Fix timezone bug: appendTimezoneOffset + toLocalDatetimeString (off-by-one day)
  - deadline_has_time: миграция, модель, схемы, сервис, ICS (all-day events), Telegram (3 места)
  - Split date/time форма: отдельные поля даты и времени, время необязательно
  - Batch mode: добавление нескольких работ за раз (общие предмет/тип, разные названия/даты)
  - formatDeadline обновлён: показывает время когда hasTime=true
  - Обновлены тесты dateUtils + DeadlinesWidget
- feat(settings): hidden subjects — per-user настройка скрытия предметов:
  - Backend: миграция (JSON column), модель, схема с валидацией (max 100, dedup, positive-only), фильтрация в schedule_filters
  - Frontend: фильтрация на 5 страницах (Schedule, Dashboard, Subjects, Works, Attendance)
  - Settings UI: карточка с toggle-кнопками, очистка стейлых ID из прошлых семестров
  - 12 новых тестов (5 auth + 7 schedule_filters), итого 631 backend
- fix: Redis distributed lock, schedule hash fix, Android widget countdown fix

## Следующие шаги (по приоритету)
- Деплой всех изменений на прод (миграции b2c3d4e5f6g8 + a1b2c3d4e5f7)
- Сборка и тестирование Android APK с fix countdown (тег `android/v*` для release)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
