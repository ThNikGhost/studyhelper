# Текущая задача

## Задача
Парсер расписания ОмГУ (HTTP API) — ЗАВЕРШЕНО ✅

## Описание
Создан парсер для автоматического получения расписания с API сайта ОмГУ.
Изначально планировался Playwright для парсинга DOM, но обнаружен скрытый JSON API.

## Критерии готовности
- [x] URL API расписания: `https://eservice.omsu.ru/schedule/backend/schedule/group/{group_id}`
- [x] HTTP парсер (httpx, без Playwright)
- [x] Маппинг данных на модель ScheduleEntry
- [x] Интеграция с backend (API endpoint POST /refresh + CLI команды)
- [x] Сохранение snapshot при парсинге
- [x] Тесты (253 всего, все проходят)
- [x] Протестировано на реальном API: **3088 записей** успешно распарсено

## Что реализовано

### API ОмГУ
- **URL**: `https://eservice.omsu.ru/schedule/backend/schedule/group/5028`
- **Формат**: JSON
- **Данные**: расписание с 04.09.2023 по 28.02.2026 (487 дней)

### Структура модуля парсера
```
backend/src/
├── parser/
│   ├── __init__.py
│   ├── exceptions.py       # ParserException, PageLoadError, etc.
│   ├── hash_utils.py       # compute_schedule_hash()
│   ├── data_mapper.py      # DataMapper class (map_api_entry, map_raw_entry)
│   └── omsu_parser.py      # OmsuScheduleParser class (HTTP)
├── cli/
│   ├── __init__.py
│   └── schedule_cli.py     # CLI commands: parse, sync
├── tasks/
│   ├── __init__.py
│   └── schedule_tasks.py   # Celery tasks (prepared)
```

### API endpoint
- `POST /api/v1/schedule/refresh?force=bool` — синхронизация расписания

### CLI команды
```bash
# Dry-run парсинг (без БД)
uv run python -m src.cli.schedule_cli parse --verbose

# JSON вывод
uv run python -m src.cli.schedule_cli parse --json

# Синхронизация с БД
uv run python -m src.cli.schedule_cli sync

# Принудительная синхронизация
uv run python -m src.cli.schedule_cli sync --force
```

### Маппинг данных API
- `time: 1-7` → реальное время (08:45-10:20, 10:30-12:05, и т.д.)
- `type_work` → LessonType enum
- `auditCorps: "4-101"` → building + room
- `week: 0/1/2` → WeekType (both/odd/even)
- `day: "DD.MM.YYYY"` → DayOfWeek (через isoweekday)

## Следующие шаги

1. **Frontend SchedulePage**
   - План готов: `docs/plans/schedule_page_frontend_plan.md`

## Заметки
- Playwright больше не нужен — используется прямой HTTP API
- API возвращает расписание на огромный период (почти 2.5 года)
- Celery задачи готовы, но не активированы (нужен Redis)
