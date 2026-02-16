# Текущая задача

## Статус
**F5.1 Widget /today endpoint задеплоен на прод. Все post-MVP фичи реализованы.**

## Последняя сессия: F5.1 Widget /today endpoint — 2026-02-16

### Сделано
- **Новый endpoint**: `GET /api/v1/widget/today?api_key=xxx` — возвращает все пары на сегодня + первую будущую пару
- **Schemas**: `TodayLessonItem`, `TodayScheduleResponse` (date, lessons[], next_lesson_from_future, next_lesson_date, cached_at)
- **Сервис**: `_build_lesson_item()`, `get_today_schedule()`, `get_today_schedule_by_token()`
- **Auth refactor**: вынесен `_authenticate_by_token()` — shared helper для обоих `*_by_token` функций
- **Scriptable JS**: переписан на `/today`, локальный `minutes_until`, 24h cache TTL, текстовые фиксы
- **Текстовые фиксы**: "Следующее занятие" → "Следующая пара", "Нет занятий" → "Нет пар", пробелы в "через X ч Y мин"
- **Edge cases**: `formatMinutesUntil(<=0)` → "Сейчас", future lesson показывает дату "Пн, 17 фев"
- **Тесты**: 14 новых (TestTodayScheduleLogic: 10, TestTodayScheduleAPI: 4), итого 43 widget тестов

### Файлы изменены
- `backend/src/schemas/widget.py` — добавлены TodayLessonItem, TodayScheduleResponse
- `backend/src/services/widget.py` — _authenticate_by_token, _build_lesson_item, get_today_schedule, get_today_schedule_by_token
- `backend/src/routers/widget.py` — GET /today endpoint
- `backend/tests/test_widget.py` — 14 новых тестов + фикстуры today_schedule_entries, _today()
- `frontend/public/scriptable-widget.js` — полный переписан на /today с offline кешем

## Следующие шаги (по приоритету)
- Все post-MVP фичи реализованы

## Блокеры / Вопросы
- Нет
