---
globs: ["**/test*/**", "**/conftest.py", "**/*_test.py", "**/test_*.py"]
description: Testing standards with pytest
---

# Testing Rules

## Фреймворк
- pytest для всех тестов
- pytest-asyncio для асинхронного кода
- pytest-cov для покрытия

## Структура тестов
```
tests/
├── conftest.py          # Общие фикстуры
├── unit/                # Юнит-тесты
│   ├── test_models.py
│   └── test_services.py
├── integration/         # Интеграционные тесты
│   └── test_api.py
└── e2e/                 # End-to-end тесты (опционально)
```

## Именование
- Файлы: `test_*.py` или `*_test.py`
- Функции: `test_что_делает_при_каких_условиях`
- Классы: `TestClassName`

### Примеры имён
```python
def test_user_creation_with_valid_data():
def test_user_creation_fails_with_empty_email():
def test_login_returns_token_for_valid_credentials():
def test_login_raises_error_for_invalid_password():
```

## Структура теста (AAA)
```python
def test_something():
    # Arrange — подготовка данных
    user = User(name="Test", email="test@example.com")
    
    # Act — выполнение действия
    result = user_service.create(user)
    
    # Assert — проверка результата
    assert result.id is not None
    assert result.name == "Test"
```

## Фикстуры
- Используй `conftest.py` для общих фикстур
- Фикстуры для БД должны откатывать транзакции
- Используй `factory_boy` или фабричные функции

```python
@pytest.fixture
def sample_user():
    return User(name="Test User", email="test@example.com")

@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session
        await session.rollback()
```

## Моки
- `pytest-mock` для мокирования
- Мокай внешние зависимости, не внутреннюю логику
- Используй `freezegun` для тестов с датами

## Покрытие
- Минимальное покрытие: 80%
- Команда: `pytest --cov=src --cov-report=term-missing`
- Критичные пути должны быть покрыты на 100%

## Асинхронные тесты
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```
