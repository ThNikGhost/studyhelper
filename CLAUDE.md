# Проект: [НАЗВАНИЕ ПРОЕКТА]

## Память проекта (автозагрузка)
@docs/PROJECT_STATUS.md
@docs/CURRENT_TASK.md

## Описание
[Краткое описание проекта — 1-2 предложения]

## Стек технологий
- **Backend**: Python 3.12+, FastAPI/Django/Flask
- **Frontend**: [уточнить позже]
- **База данных**: PostgreSQL на облачном сервере
- **CI/CD**: GitHub Actions → деплой на облачный сервер

## Структура проекта
```
/
├── src/                 # Исходный код
├── tests/               # Тесты
├── docs/                # Документация
│   └── tasks/           # Задачи в формате .md
├── scripts/             # Вспомогательные скрипты
└── .github/workflows/   # CI/CD пайплайны
```

## Команды

### Разработка
```bash
# Создание виртуального окружения и установка зависимостей
uv sync

# Добавление зависимости
uv add fastapi
uv add --dev pytest ruff

# Запуск dev-сервера
uv run python -m src.main
# или
uv run uvicorn src.main:app --reload

# Запуск тестов
uv run pytest

# Линтинг
uv run ruff check .
uv run ruff format .
```

### Git
```bash
# Новая фича
git checkout -b feature/название

# Коммит
git add .
git commit -m "feat(scope): description"

# Пуш и PR
git push -u origin feature/название
```

## Соглашения

### Python
- Форматирование: Ruff (или Black + isort)
- Линтинг: Ruff
- Type hints обязательны
- Docstrings в формате Google

### Тестирование
- Используем pytest
- Минимальное покрытие: 80%
- Тесты рядом с кодом в папке tests/

## Сервер (облако)
- **Адрес**: [IP или домен]
- **SSH пользователь**: [user]
- **Путь к проекту**: /home/[user]/[project]
- **Сервис**: systemd unit `[project].service`

### Проверка статуса
```bash
# Статус сервиса
sudo systemctl status [project]

# Логи
sudo journalctl -u [project] -f

# Статус БД
sudo systemctl status postgresql
```

## Важные файлы
- `pyproject.toml` — конфигурация проекта и зависимости
- `uv.lock` — lock-файл зависимостей (коммитится!)
- `src/config.py` — конфигурация приложения
- `src/database.py` — подключение к БД
- `.env` — переменные окружения (НЕ КОММИТИТЬ!)

## Текущие задачи
См. `docs/PROJECT_STATUS.md` и `docs/CURRENT_TASK.md`

## Принятые решения
См. `docs/DECISIONS.md`

## Команды сессии
- `/session-start` — начать сессию (прочитать контекст)
- `/session-end` — завершить сессию (сохранить контекст)
- `/commit` — коммит и пуш на GitHub

## Правило: Коммиты
После завершения важной фичи, исправления бага или логического блока работы:
1. Проверь тесты: `uv run pytest -q`
2. Проверь линтер: `uv run ruff check .`
3. Сделай коммит и пуш: `/commit`

Не накапливай много изменений — коммить часто и атомарно.
