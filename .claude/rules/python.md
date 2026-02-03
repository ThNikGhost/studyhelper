# Python Code Rules

## Менеджер зависимостей: uv
- Используем `uv` для управления зависимостями и виртуальным окружением
- Зависимости описаны в `pyproject.toml`
- Lock-файл: `uv.lock` (коммитится в git)

### Основные команды
```bash
uv sync              # Установить зависимости из lock-файла
uv add package       # Добавить зависимость
uv add --dev package # Добавить dev-зависимость
uv remove package    # Удалить зависимость
uv run command       # Запустить команду в виртуальном окружении
```

## Стиль кода
- Форматирование: Ruff (совместим с Black)
- Максимальная длина строки: 88 символов
- Используй одинарные кавычки для строк
- Сортировка импортов: isort-совместимая (через Ruff)

## Type Hints
- Обязательны для всех функций и методов
- Используй `from __future__ import annotations` для forward references
- Для опциональных значений: `str | None` вместо `Optional[str]`
- Для коллекций: `list[str]` вместо `List[str]` (Python 3.9+)

## Docstrings
- Формат: Google style
- Обязательны для публичных функций, классов, модулей
- Пример:
  ```python
  def process_data(items: list[str], limit: int = 10) -> dict[str, int]:
      """Process a list of items and return statistics.
      
      Args:
          items: List of items to process.
          limit: Maximum number of items to process.
          
      Returns:
          Dictionary with processing statistics.
          
      Raises:
          ValueError: If items list is empty.
      """
  ```

## Структура файла
1. Module docstring
2. `from __future__ import annotations`
3. Standard library imports
4. Third-party imports
5. Local imports
6. Constants
7. Classes
8. Functions
9. `if __name__ == "__main__":` block

## Именование
- Классы: `PascalCase`
- Функции и переменные: `snake_case`
- Константы: `UPPER_SNAKE_CASE`
- Приватные атрибуты: `_leading_underscore`
- "Магические" методы: `__dunder__`

## Обработка ошибок
- Используй конкретные исключения, не голый `except:`
- Создавай кастомные исключения для бизнес-логики
- Логируй ошибки через `logging`, не `print()`
