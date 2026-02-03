# План разработки Backend — StudyHelper

## Технологии

| Компонент | Технология |
|-----------|------------|
| Фреймворк | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Драйвер БД | asyncpg |
| Миграции | Alembic |
| Валидация | Pydantic v2 |
| Аутентификация | JWT (python-jose) |
| Хеширование паролей | passlib[bcrypt] |
| Фоновые задачи | Celery + Redis |
| Парсинг | Playwright |
| Push-уведомления | pywebpush |
| Тестирование | pytest + pytest-asyncio |
| Линтинг | Ruff |

---

## Структура проекта

```
backend/
├── pyproject.toml           # Зависимости и конфигурация
├── alembic.ini              # Конфигурация Alembic
├── alembic/                 # Миграции
│   ├── env.py
│   └── versions/
├── src/
│   ├── __init__.py
│   ├── main.py              # Точка входа FastAPI
│   ├── config.py            # Настройки приложения
│   ├── database.py          # Подключение к БД
│   ├── dependencies.py      # Общие зависимости (get_db, get_current_user)
│   │
│   ├── models/              # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── base.py          # Base, mixins
│   │   ├── user.py
│   │   ├── semester.py
│   │   ├── subject.py
│   │   ├── schedule.py
│   │   ├── work.py
│   │   ├── teacher.py
│   │   ├── university.py
│   │   └── classmate.py
│   │
│   ├── schemas/             # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── semester.py
│   │   ├── subject.py
│   │   ├── schedule.py
│   │   ├── work.py
│   │   ├── teacher.py
│   │   ├── university.py
│   │   └── classmate.py
│   │
│   ├── routers/             # API роутеры
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── semesters.py
│   │   ├── subjects.py
│   │   ├── schedule.py
│   │   ├── works.py
│   │   ├── teachers.py
│   │   ├── university.py
│   │   └── classmates.py
│   │
│   ├── services/            # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── schedule_parser.py
│   │   └── ...
│   │
│   ├── utils/               # Утилиты
│   │   ├── __init__.py
│   │   ├── security.py      # JWT, хеширование
│   │   └── exceptions.py    # Кастомные исключения
│   │
│   └── tasks/               # Celery задачи (Phase 2)
│       ├── __init__.py
│       └── schedule.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py          # Фикстуры
    ├── test_auth.py
    ├── test_subjects.py
    └── ...
```

---

## Этапы разработки

### Этап 1: Инициализация проекта
**Приоритет:** Критический

- [ ] Создать структуру папок
- [ ] Настроить `pyproject.toml` с зависимостями
- [ ] Настроить Ruff (линтер)
- [ ] Создать `src/config.py` — загрузка .env
- [ ] Создать `src/database.py` — async подключение
- [ ] Создать `src/main.py` — базовое FastAPI приложение
- [ ] Настроить Alembic для миграций
- [ ] Создать базовую модель `src/models/base.py`

**Зависимости для установки:**
```
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
alembic
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
python-multipart
```

---

### Этап 2: Аутентификация
**Приоритет:** Критический

- [ ] Модель `User`
- [ ] Схемы: `UserCreate`, `UserLogin`, `UserResponse`, `Token`
- [ ] Сервис `auth.py`:
  - `create_user()` — с проверкой на макс 2 пользователя
  - `authenticate_user()`
  - `create_access_token()`
  - `create_refresh_token()`
- [ ] Утилиты `security.py`:
  - `hash_password()`
  - `verify_password()`
  - `create_token()`
  - `decode_token()`
- [ ] Роутер `auth.py`:
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /auth/refresh`
  - `POST /auth/logout`
  - `GET /auth/me`
- [ ] Dependency `get_current_user`
- [ ] Тесты для аутентификации

---

### Этап 3: Семестры
**Приоритет:** Высокий (нужен для subjects)

- [ ] Модель `Semester`
- [ ] Схемы: `SemesterCreate`, `SemesterUpdate`, `SemesterResponse`
- [ ] Роутер `semesters.py`:
  - `GET /semesters`
  - `POST /semesters`
  - `GET /semesters/current`
  - `PUT /semesters/{id}`
  - `DELETE /semesters/{id}`
  - `PUT /semesters/{id}/set-current`
- [ ] Миграция
- [ ] Тесты

---

### Этап 4: Предметы
**Приоритет:** Высокий

- [ ] Модель `Subject`
- [ ] Схемы: `SubjectCreate`, `SubjectUpdate`, `SubjectResponse`
- [ ] Роутер `subjects.py`:
  - `GET /subjects`
  - `POST /subjects`
  - `GET /subjects/{id}`
  - `PUT /subjects/{id}`
  - `DELETE /subjects/{id}`
  - `GET /subjects/{id}/works`
- [ ] Фильтрация по семестру
- [ ] Миграция
- [ ] Тесты

---

### Этап 5: Учебные работы
**Приоритет:** Критический

- [ ] Модели: `Work`, `WorkStatus`, `WorkStatusHistory`
- [ ] Схемы для всех моделей
- [ ] Роутер `works.py`:
  - `GET /works` — с фильтрами (subject, status, deadline)
  - `POST /works`
  - `GET /works/{id}`
  - `PUT /works/{id}`
  - `DELETE /works/{id}`
  - `PUT /works/{id}/status` — изменение статуса текущего пользователя
  - `GET /works/{id}/history`
  - `GET /works/upcoming` — ближайшие дедлайны
- [ ] Логика парного режима: WorkStatus создаётся для каждого пользователя
- [ ] Автоматическое создание записи в history при изменении статуса
- [ ] Миграции
- [ ] Тесты

---

### Этап 6: Преподаватели
**Приоритет:** Средний

- [ ] Модель `Teacher`
- [ ] Схемы: `TeacherCreate`, `TeacherUpdate`, `TeacherResponse`
- [ ] Роутер `teachers.py`:
  - `GET /teachers`
  - `POST /teachers`
  - `GET /teachers/{id}`
  - `PUT /teachers/{id}`
  - `DELETE /teachers/{id}`
- [ ] Миграция
- [ ] Тесты

---

### Этап 7: Информация об университете
**Приоритет:** Низкий

- [ ] Модели: `Department`, `Building`
- [ ] Схемы
- [ ] Роутер `university.py`:
  - CRUD для departments
  - CRUD для buildings
- [ ] Миграции
- [ ] Тесты

---

### Этап 8: Одногруппники
**Приоритет:** Низкий

- [ ] Модель `Classmate`
- [ ] Схемы
- [ ] Роутер `classmates.py`:
  - CRUD операции
  - `POST /classmates/{id}/photo` — загрузка фото
- [ ] Миграция
- [ ] Тесты

---

### Этап 9: Расписание
**Приоритет:** Критический

- [ ] Модели: `ScheduleEntry`, `ScheduleSnapshot`
- [ ] Схемы
- [ ] Сервис `schedule_parser.py`:
  - Парсинг с помощью Playwright
  - Извлечение данных из DOM
  - Хеширование для определения изменений
- [ ] Роутер `schedule.py`:
  - `GET /schedule` — на неделю
  - `GET /schedule/today`
  - `GET /schedule/current` — текущая/следующая пара
  - `POST /schedule/refresh` — принудительное обновление
- [ ] Миграции
- [ ] Тесты (с мок-данными)

---

### Этап 10: Celery задачи (опционально для MVP)
**Приоритет:** Средний

- [ ] Настройка Celery + Redis
- [ ] Задача автоматического обновления расписания
- [ ] Celery Beat для периодических задач

---

## API Versioning

Все эндпоинты под префиксом `/api/v1/`:

```python
# main.py
from fastapi import FastAPI
from src.routers import auth, subjects, works, ...

app = FastAPI(title="StudyHelper API", version="1.0.0")

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_v1.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
# ...

app.include_router(api_v1)
```

---

## Примеры кода

### config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

### database.py
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session
```

### models/base.py
```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
```

---

## Тестирование

### Структура тестов
```
tests/
├── conftest.py      # Фикстуры: test_db, test_client, auth_headers
├── test_auth.py     # Тесты регистрации, логина
├── test_subjects.py # CRUD тесты для предметов
├── test_works.py    # Тесты работ + парный режим
└── ...
```

### Запуск тестов
```bash
uv run pytest -v
uv run pytest --cov=src --cov-report=term-missing
```

---

## Чеклист готовности MVP Backend

- [ ] Все модели созданы и мигрированы
- [ ] Аутентификация работает (register, login, refresh, me)
- [ ] CRUD для всех сущностей MVP
- [ ] Парный режим для WorkStatus
- [ ] Парсер расписания работает
- [ ] Тесты покрывают >= 80% кода
- [ ] Линтер проходит без ошибок
- [ ] API документация доступна на /docs
