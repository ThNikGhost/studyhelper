# Текущая задача

## Задача
Парсер расписания ОмГУ (Playwright)

## Описание
Создать парсер для автоматического получения расписания с сайта ОмГУ.
Это нужно сделать до реализации SchedulePage, чтобы понять реальную структуру данных.

## Критерии готовности
- [x] URL сайта расписания уже в конфиге (`settings.schedule_url`)
- [x] Создать Playwright скрипт для парсинга
- [x] Маппинг данных на модель ScheduleEntry
- [x] Интеграция с backend (API endpoint POST /refresh + CLI команды)
- [x] Сохранение snapshot при парсинге
- [x] Тесты парсера (85 новых тестов)

## Прогресс
- [x] Playwright парсер (`src/parser/`)
- [x] Интеграция с backend
- [x] CLI команды (`src/cli/schedule_cli.py`)
- [x] Celery задачи подготовлены (`src/tasks/schedule_tasks.py`)
- [x] Тесты (253 всего, все проходят)

## Что реализовано

### Структура модуля парсера
```
backend/src/
├── parser/
│   ├── __init__.py
│   ├── exceptions.py       # ParserException, PageLoadError, etc.
│   ├── hash_utils.py       # compute_schedule_hash()
│   ├── data_mapper.py      # DataMapper class
│   └── omsu_parser.py      # OmsuScheduleParser class
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
uv run python -m src.cli.schedule_cli parse --verbose --visible

# Синхронизация с БД
uv run python -m src.cli.schedule_cli sync

# Принудительная синхронизация
uv run python -m src.cli.schedule_cli sync --force
```

## Следующие шаги

1. **Тестирование парсера на реальном сайте**
   - Установить Playwright браузер: `uv run playwright install chromium`
   - Запустить парсинг: `uv run python -m src.cli.schedule_cli parse --visible --verbose`
   - Адаптировать селекторы под реальную структуру DOM

2. **Frontend SchedulePage**
   - План готов: `docs/plans/schedule_page_frontend_plan.md`

## Заметки
- Селекторы DOM в `omsu_parser.py` — generic, могут потребовать адаптации
- Windows asyncio policy установлена в CLI и парсере
- Celery задачи готовы, но не активированы (нужен Redis)
