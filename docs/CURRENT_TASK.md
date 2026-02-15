# Текущая задача

## Статус
**F5 Phone Widgets задеплоен на прод. Все post-MVP фичи реализованы.**

## Последняя сессия: F5 Phone Widgets — 2026-02-15

### Сделано
- **Рефакторинг**: вынесена `filter_entries_by_user_prefs()` из `calendar_feed.py` → `utils/schedule_filters.py` (shared)
- **Модель WidgetApiKey**: per-user token (secrets.token_urlsafe(48)), unique indexes на token и user_id
- **Миграция**: `02665a1d4d94_add_widget_api_keys_table` (down_revision: d01120901766)
- **Schemas**: WidgetApiKeyStatusResponse, WidgetApiKeyCreateResponse, NextLessonResponse
- **Сервис**: Token CRUD (create/regenerate/revoke/update_last_used) + get_next_lesson (lookahead 7 дней, фильтрация по подгруппе/физкультуре)
- **Роутер**: 4 endpoints — GET /status (JWT), POST /enable (JWT), DELETE /disable (JWT), GET /next-lesson?api_key=xxx (public, rate limit 60/min)
- **Frontend**: SettingsPage секция "Виджеты" (Smartphone icon, indigo) с API ключом, URL, Copy, инструкции iOS/Android
- **Scriptable JS**: `frontend/public/scriptable-widget.js` — виджет для iOS (Keychain, offline cache, ListWidget)
- **Тесты**: 29 backend тестов (Token CRUD: 7, Next Lesson Logic: 11, API: 11)

### Файлы созданы
- `backend/src/utils/schedule_filters.py` — shared фильтр расписания
- `backend/src/models/widget_api_key.py` — модель WidgetApiKey
- `backend/src/schemas/widget.py` — Pydantic schemas
- `backend/src/services/widget.py` — сервис (CRUD + next lesson)
- `backend/src/routers/widget.py` — 4 endpoint-а
- `backend/alembic/versions/02665a1d4d94_add_widget_api_keys_table.py` — миграция
- `backend/tests/test_widget.py` — 29 тестов
- `frontend/src/types/widget.ts` — TypeScript типы
- `frontend/src/services/widgetService.ts` — API сервис
- `frontend/public/scriptable-widget.js` — Scriptable виджет для iOS

### Файлы изменены
- `backend/src/services/calendar_feed.py` — import shared filter, удалён _filter_entries
- `backend/src/models/user.py` — relationship widget_api_key
- `backend/src/models/__init__.py` — регистрация WidgetApiKey
- `backend/src/main.py` — подключение widget router
- `frontend/src/pages/SettingsPage.tsx` — секция "Виджеты" + модальное окно удаления

## Следующие шаги (по приоритету)
- Все post-MVP фичи реализованы

## Блокеры / Вопросы
- Нет
