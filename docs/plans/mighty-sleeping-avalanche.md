# План: Парсер расписания ОмГУ

## Цель
Создать Playwright парсер для автоматического получения расписания с сайта eservice.omsu.ru и интеграции с существующим Schedule модулем.

## Исходные данные

- **URL**: `https://eservice.omsu.ru/schedule/#/schedule/group/5028` (уже в config.py)
- **Тип сайта**: SPA (Single Page Application), API недоступен
- **Инструмент**: Playwright (уже в зависимостях: `playwright>=1.49.0`)
- **ID группы**: 5028

## Структура файлов

```
backend/src/
├── parser/                      # Новый модуль
│   ├── __init__.py
│   ├── omsu_parser.py           # Playwright парсер
│   ├── data_mapper.py           # Маппинг данных → ScheduleEntryCreate
│   ├── hash_utils.py            # SHA-256 хеширование для отслеживания изменений
│   └── exceptions.py            # Кастомные исключения
├── cli/                         # CLI команды
│   ├── __init__.py
│   └── schedule_cli.py          # Команда для ручного запуска
├── tasks/                       # Celery задачи (подготовка)
│   ├── __init__.py
│   └── schedule_tasks.py
└── services/
    └── schedule.py              # Добавить: sync_schedule()
```

## Этапы реализации

### Этап 1: Исследование DOM структуры сайта
**Действия:**
1. Открыть https://eservice.omsu.ru/schedule/#/schedule/group/5028
2. В DevTools (F12) изучить:
   - Network tab: проверить XHR/Fetch запросы (возможно есть скрытый API)
   - Elements tab: найти CSS селекторы для данных
3. Задокументировать селекторы для:
   - Дни недели
   - Время пар (начало-конец)
   - Название предмета
   - Тип занятия (лекция/практика/лаб)
   - Преподаватель
   - Аудитория/корпус
   - Чётная/нечётная неделя
   - Подгруппы

### Этап 2: Модуль парсера

#### 2.1 `parser/exceptions.py`
```python
class ParserException(Exception): ...
class PageLoadError(ParserException): ...
class ElementNotFoundError(ParserException): ...
class DataExtractionError(ParserException): ...
class MappingError(ParserException): ...
```

#### 2.2 `parser/hash_utils.py`
- `compute_schedule_hash(entries: list[dict]) -> str` — SHA-256 для сравнения расписаний

#### 2.3 `parser/data_mapper.py`
- Словари маппинга: дни недели (рус → int), типы занятий (рус → LessonType)
- `parse_time(str) -> time`
- `parse_lesson_type(str) -> LessonType`
- `parse_week_type(str) -> WeekType | None`
- `map_raw_entry_to_schema(dict) -> ScheduleEntryCreate`

#### 2.4 `parser/omsu_parser.py`
```python
class OmsuScheduleParser:
    async def __aenter__(self) -> self  # Запуск Playwright
    async def __aexit__(...) -> None    # Закрытие браузера
    async def parse(url: str | None) -> ParseResult

class ParseResult:
    entries: list[ScheduleEntryCreate]
    raw_data: list[dict]
    content_hash: str
    source_url: str
    parsed_date: date
```

### Этап 3: Расширение сервиса

**Файл:** `services/schedule.py` — добавить:

```python
async def parse_schedule(url: str | None = None) -> ParseResult:
    """Parse schedule using Playwright."""

async def sync_schedule(db: AsyncSession, force: bool = False) -> dict:
    """Sync schedule: parse, compare hash, update if changed."""

async def _clear_schedule_entries(db: AsyncSession) -> None:
    """Delete all entries before sync."""
```

### Этап 4: Обновление роутера

**Файл:** `routers/schedule.py` — реализовать плейсхолдер:

```python
@router.post("/refresh")
async def refresh_schedule(
    force: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return await schedule_service.sync_schedule(db, force)
```

### Этап 5: CLI команда

**Файл:** `cli/schedule_cli.py`

```bash
# Dry-run парсинг (без сохранения в БД)
uv run python -m src.cli.schedule_cli parse --verbose

# Синхронизация с БД
uv run python -m src.cli.schedule_cli sync

# Принудительная синхронизация
uv run python -m src.cli.schedule_cli sync --force
```

### Этап 6: Celery задачи (подготовка)

**Файл:** `tasks/schedule_tasks.py`
- Задача `sync_schedule_task(force: bool)`
- Конфиг для периодического запуска каждые 6 часов (закомментирован до настройки Celery)

### Этап 7: Тесты

**Файл:** `tests/test_parser.py`
- Тесты hash_utils: одинаковые данные → одинаковый хеш
- Тесты data_mapper: парсинг времени, типов занятий, дней недели
- Тесты OmsuScheduleParser: context manager (с моками Playwright)

**Файл:** `tests/test_schedule_sync.py`
- POST /refresh success
- POST /refresh unchanged (хеш совпадает)
- POST /refresh force=true
- POST /refresh error handling

## Критические файлы

| Файл | Действие |
|------|----------|
| `backend/src/parser/__init__.py` | Создать |
| `backend/src/parser/exceptions.py` | Создать |
| `backend/src/parser/hash_utils.py` | Создать |
| `backend/src/parser/data_mapper.py` | Создать |
| `backend/src/parser/omsu_parser.py` | Создать |
| `backend/src/cli/__init__.py` | Создать |
| `backend/src/cli/schedule_cli.py` | Создать |
| `backend/src/tasks/__init__.py` | Создать |
| `backend/src/tasks/schedule_tasks.py` | Создать |
| `backend/src/services/schedule.py` | Расширить |
| `backend/src/routers/schedule.py` | Обновить |
| `backend/pyproject.toml` | Добавить CLI script |
| `backend/tests/test_parser.py` | Создать |
| `backend/tests/test_schedule_sync.py` | Создать |

## Команды установки

```bash
cd backend

# Установить зависимости парсера
uv sync --group parser

# Установить браузер Playwright
uv run playwright install chromium
```

## Верификация

1. **Тесты парсера:**
   ```bash
   uv run pytest tests/test_parser.py -v
   ```

2. **Dry-run парсинг:**
   ```bash
   uv run python -m src.cli.schedule_cli parse --verbose --visible
   ```
   Ожидание: список всех пар с названиями, временем, преподавателями

3. **Синхронизация:**
   ```bash
   uv run python -m src.cli.schedule_cli sync
   ```
   Ожидание: записи в БД, создан snapshot

4. **API endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/schedule/refresh \
     -H "Authorization: Bearer <token>"
   ```
   Ожидание: `{"success": true, "changed": true, "entries_count": N}`

5. **Полный цикл тестов:**
   ```bash
   uv run pytest -v
   ```

## Windows-специфика

- Использовать `WindowsSelectorEventLoopPolicy` для asyncio в CLI
- Playwright работает корректно на Windows

## Заметки

- Селекторы DOM будут определены на этапе 1 (исследование сайта)
- Celery задачи подготовлены, но не активированы (нужен Redis)
- Группа пользователя (5028) уже в config.py, можно параметризовать позже
