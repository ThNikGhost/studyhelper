# Текущая задача

## Статус
**F4 iCalendar feed задеплоен на прод. Следующая: F5 (Phone widgets).**

## Последняя сессия: F4 iCalendar (.ics) Feed — 2026-02-15

### Сделано
- **Модель CalendarFeed**: per-user token (secrets.token_urlsafe(48)), unique indexes на token и user_id
- **Сервис**: Token CRUD (create/regenerate/revoke/get) + ICS генерация (schedule + deadlines)
- **ICS генерация**: VCALENDAR с VEVENT для schedule entries + work deadlines, VALARM (24h и 1h), REFRESH-INTERVAL PT6H
- **Фильтрация**: по subgroup и PE teacher (из user preferences)
- **Роутер**: 4 endpoints — GET /status (JWT), POST /enable (JWT), DELETE /disable (JWT), GET /feed/{token}.ics (public, rate limit 30/min)
- **Frontend**: SettingsPage секция "Подписка на календарь" с Copy URL, регенерация, отключение
- **Тесты**: 27 backend тестов (Token CRUD: 7, ICS Generation: 9, API: 11)
- **Code review fixes**: base_url в config.py (вместо hardcoded domain), throttle last_accessed_at (1 раз/час)
- **Deploy**: Миграция d01120901766 применена, контейнеры пересобраны, endpoints работают

### Файлы созданы
- `backend/src/models/calendar_feed.py` — модель CalendarFeed
- `backend/src/schemas/calendar_feed.py` — Pydantic schemas
- `backend/src/services/calendar_feed.py` — сервис (CRUD + ICS)
- `backend/src/routers/calendar_feed.py` — 4 endpoint-а
- `backend/alembic/versions/d01120901766_add_calendar_feeds_table.py` — миграция
- `backend/tests/test_calendar_feed.py` — 27 тестов
- `frontend/src/types/calendar.ts` — TypeScript типы
- `frontend/src/services/calendarFeedService.ts` — API сервис

### Файлы изменены
- `backend/pyproject.toml` — добавлена зависимость icalendar>=7.0.0
- `backend/src/models/user.py` — relationship calendar_feed
- `backend/src/models/__init__.py` — регистрация CalendarFeed
- `backend/src/main.py` — подключение calendar_feed router
- `backend/src/config.py` — добавлен base_url setting
- `frontend/src/pages/SettingsPage.tsx` — секция "Подписка на календарь"

## Следующие шаги (по приоритету)
1. **F5** — Phone widgets

## Блокеры / Вопросы
- Нет
