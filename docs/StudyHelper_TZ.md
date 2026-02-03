# Техническое задание: StudyHelper

## Краткое описание проекта

**StudyHelper** — персональное PWA-приложение для студентов ОмГУ им. Ф.М. Достоевского, объединяющее расписание (с автоматическим парсингом), отслеживание дедлайнов и учебных работ, хранение файлов, информацию о преподавателях, группе и университете. Приложение поддерживает парный режим для двух пользователей с возможностью видеть прогресс друг друга и отправляет push-уведомления о важных событиях.

---

## Инструкции для Claude Code

После прочтения данного ТЗ выполни следующие действия:

### 1. Создай/обнови структуру проекта

```
StudyHelper/
├── CLAUDE.md                 # Обнови под актуальную информацию проекта
├── Current_task.md           # Текущая задача
├── Decisions.md              # Архитектурные решения
├── project_status.md         # Статус проекта
├── plans/
│   ├── MVP_plan.md           # План MVP
│   ├── full_plan.md          # Полный план разработки
│   └── future_features.md    # Планы на будущее
├── docs/
│   ├── API.md                # Документация API
│   ├── database_schema.md    # Схема БД
│   └── deployment.md         # Инструкции по деплою
├── frontend/                 # PWA Frontend
├── backend/                  # Python Backend
└── docker/                   # Docker конфигурация
```

### 2. Заполни файлы

#### CLAUDE.md
Должен содержать:
- Название проекта и краткое описание (1-2 предложения)
- Технический стек (frontend, backend, БД)
- Команды для запуска (dev, build, test)
- Структура проекта (краткая)
- Текущий статус разработки
- Ссылки на ключевые файлы (ТЗ, планы, документация)

#### Current_task.md
- Текущая задача: "Инициализация проекта и настройка окружения"
- Чеклист подзадач
- Блокеры (если есть)
- Следующие шаги

#### Decisions.md
- Выбор фреймворков с обоснованием
- Архитектурные решения (структура API, разделение данных)
- Структура БД (ключевые таблицы)
- Принципы разработки

#### project_status.md
- Общий прогресс (% выполнения)
- Что сделано (список)
- Что в работе
- Что запланировано
- Блокеры и риски

---

## Технические требования

### Стек технологий

| Компонент | Технология | Обоснование |
|-----------|------------|-------------|
| **Frontend** | React + TypeScript + Vite | Современный стек, хорошая поддержка PWA, большое сообщество |
| **UI библиотека** | Tailwind CSS + shadcn/ui | Быстрая разработка, кастомизация под брендбук |
| **State Management** | Zustand или React Query | Лёгкий, без бойлерплейта |
| **PWA** | Workbox (vite-plugin-pwa) | Надёжное кеширование, offline-режим |
| **Backend** | Python + FastAPI | Быстрый, асинхронный, автодокументация API |
| **БД** | PostgreSQL | Надёжная, поддержка JSON, хорошая производительность |
| **ORM** | SQLAlchemy 2.0 + asyncpg | Стандарт для Python, async поддержка |
| **Миграции** | Alembic | Стандарт для SQLAlchemy |
| **Парсинг** | Playwright | Работает с JS-рендерингом (сайт расписания использует JS) |
| **Фоновые задачи** | Celery + Redis | Парсинг расписания, отправка уведомлений |
| **Push-уведомления** | Web Push API + pywebpush | Стандарт для PWA |
| **Аутентификация** | JWT (python-jose) | Простая, stateless |
| **Валидация** | Pydantic v2 | Встроена в FastAPI |
| **Контейнеризация** | Docker + Docker Compose | Упрощает деплой |

### Дизайн-система

#### Цвета (брендбук ОмГУ)

```css
:root {
  /* Основные цвета ОмГУ */
  --color-primary: #8B0000;      /* Тёмно-красный */
  --color-secondary: #FF6B00;    /* Оранжевый */
  
  /* Нейтральные */
  --color-black: #1A1A1A;
  --color-gray-dark: #4A4A4A;
  --color-gray: #9A9A9A;
  --color-gray-light: #E5E5E5;
  --color-white: #FFFFFF;
  
  /* Семантические */
  --color-success: #22C55E;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
  
  /* Тёмная тема */
  --color-bg-dark: #121212;
  --color-surface-dark: #1E1E1E;
  --color-text-dark: #E5E5E5;
}
```

#### Типографика
- **Заголовки:** Inter или system-ui
- **Основной текст:** Inter или system-ui
- **Размеры:** 14px base, scale 1.25

#### Компоненты
- Скруглённые углы: `border-radius: 12px` (карточки), `8px` (кнопки, инпуты)
- Тени: subtle, не агрессивные
- Анимации: 200ms ease-out

---

## Функциональные модули

### 1. Аутентификация

#### Требования
- Регистрация/вход по email + пароль
- JWT токены (access 15min + refresh 7days)
- Только 2 пользователя в системе (проверка при регистрации)
- Сессии на нескольких устройствах

#### API Endpoints
```
POST /api/auth/register     # Регистрация
POST /api/auth/login        # Вход
POST /api/auth/refresh      # Обновление токена
POST /api/auth/logout       # Выход
GET  /api/auth/me           # Текущий пользователь
```

#### Модель данных
```python
class User:
    id: int (PK)
    email: str (unique)
    password_hash: str
    name: str
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime
```

---

### 2. Расписание

#### Требования
- Парсинг с https://eservice.omsu.ru/schedule/#/schedule/group/5028
- Поддержка чередующихся недель (чётная/нечётная или кастомная)
- Автоматическое обновление (cron: каждые 6 часов)
- Ручное обновление по кнопке
- Push-уведомление при изменении расписания
- Отображение текущей/следующей пары с таймером
- Возможность парсить расписание преподавателя (в будущем)

#### Логика парсинга
Сайт https://eservice.omsu.ru использует JavaScript для рендеринга. Нужен Playwright:
1. Открыть страницу с Playwright
2. Дождаться загрузки данных (селектор или networkidle)
3. Извлечь данные из DOM или перехватить API-запросы браузера
4. Распарсить структуру: день недели, время, предмет, преподаватель, аудитория, тип недели
5. Сохранить в БД
6. Сравнить хеш с предыдущей версией → уведомление если изменилось

#### API Endpoints
```
GET  /api/schedule                    # Расписание на неделю
GET  /api/schedule/today              # Расписание на сегодня
GET  /api/schedule/current            # Текущая/следующая пара
POST /api/schedule/refresh            # Принудительное обновление
```

#### Модель данных
```python
class ScheduleEntry:
    id: int (PK)
    day_of_week: int (0-6, 0=понедельник)
    week_type: str | None          # "odd", "even", null (каждую неделю)
    time_start: time
    time_end: time
    subject_id: int (FK) | None
    subject_name: str              # Название из парсинга
    teacher_id: int (FK) | None
    teacher_name: str | None
    room: str | None
    entry_type: str                # "lecture", "practice", "lab"
    created_at: datetime
    updated_at: datetime

class ScheduleSnapshot:
    id: int (PK)
    hash: str                      # MD5 хеш для сравнения
    data: JSON
    parsed_at: datetime
```

---

### 3. Предметы

#### Требования
- CRUD операции
- Типы занятий: лекции, практики, лабораторные, практика
- Типы контроля: контрольные, коллоквиумы, экзамены, зачёты (простые/дифф)
- Система оценок: 1-5 или баллы (настраивается per-предмет)
- Требования к автомату (текстовое поле)
- Заметки по предмету
- Привязка файлов
- Расчёт прогресса по работам

#### API Endpoints
```
GET    /api/subjects                  # Список предметов
POST   /api/subjects                  # Создать предмет
GET    /api/subjects/{id}             # Получить предмет
PUT    /api/subjects/{id}             # Обновить предмет
DELETE /api/subjects/{id}             # Удалить предмет
GET    /api/subjects/{id}/progress    # Прогресс по предмету
GET    /api/subjects/{id}/works       # Работы по предмету
GET    /api/subjects/{id}/files       # Файлы по предмету
```

#### Модель данных
```python
class Subject:
    id: int (PK)
    name: str
    short_name: str | None
    semester_id: int (FK)
    control_type: str              # "exam", "credit", "diff_credit"
    grading_system: str            # "standard" (1-5), "points"
    max_points: int | None
    auto_requirements: str | None  # Текст требований к автомату
    notes: str | None
    color: str | None
    created_at: datetime
    updated_at: datetime
```

---

### 4. Учебные работы

#### Требования
- Типы: ДЗ, лабораторная, контрольная, коллоквиум, курсовая, реферат
- Статусы: не начато → в работе → сдано
- Приоритеты: высокий, средний, низкий
- Дедлайны
- История изменений статуса
- Привязка к предмету
- **Отдельный статус для каждого пользователя** (парный режим)

#### API Endpoints
```
GET    /api/works                     # Список работ
POST   /api/works                     # Создать работу
GET    /api/works/{id}                # Получить работу
PUT    /api/works/{id}                # Обновить работу
DELETE /api/works/{id}                # Удалить работу
PUT    /api/works/{id}/status         # Изменить статус
GET    /api/works/{id}/history        # История изменений
GET    /api/works/upcoming            # Ближайшие дедлайны
```

#### Модель данных
```python
class Work:
    id: int (PK)
    subject_id: int (FK)
    title: str
    description: str | None
    work_type: str                 # "homework", "lab", "test", "colloquium", "coursework", "essay"
    deadline: datetime | None
    priority: str                  # "high", "medium", "low"
    created_at: datetime
    updated_at: datetime

class WorkStatus:
    id: int (PK)
    work_id: int (FK)
    user_id: int (FK)
    status: str                    # "not_started", "in_progress", "done"
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

class WorkStatusHistory:
    id: int (PK)
    work_status_id: int (FK)
    old_status: str | None
    new_status: str
    changed_at: datetime
```

---

### 5. Посещаемость

#### Требования
- По умолчанию пара считается посещённой после её окончания
- Ручная отметка пропуска
- Статистика: посетил X из Y пар
- Привязка к пользователю

#### API Endpoints
```
GET  /api/attendance                       # Посещаемость
POST /api/attendance/mark-absent           # Отметить пропуск
POST /api/attendance/mark-present          # Отменить пропуск
GET  /api/attendance/stats                 # Статистика
GET  /api/attendance/stats/{subject_id}    # Статистика по предмету
```

#### Модель данных
```python
class Attendance:
    id: int (PK)
    user_id: int (FK)
    schedule_entry_id: int (FK)
    date: date
    is_present: bool (default: True)
    created_at: datetime
    updated_at: datetime
```

---

### 6. Преподаватели

#### Требования
- CRUD операции
- Контакты: email, телефон, Telegram, VK
- Кабинет (опционально)
- Ссылка на расписание
- Быстрые кнопки связи

#### API Endpoints
```
GET    /api/teachers                  # Список преподавателей
POST   /api/teachers                  # Создать
GET    /api/teachers/{id}             # Получить
PUT    /api/teachers/{id}             # Обновить
DELETE /api/teachers/{id}             # Удалить
```

#### Модель данных
```python
class Teacher:
    id: int (PK)
    last_name: str
    first_name: str
    middle_name: str | None
    email: str | None
    phone: str | None
    telegram: str | None
    vk: str | None
    room: str | None
    schedule_url: str | None
    created_at: datetime
    updated_at: datetime
```

---

### 7. Информация об университете

#### API Endpoints
```
GET/POST/PUT/DELETE /api/university/departments
GET/POST/PUT/DELETE /api/university/buildings
```

#### Модель данных
```python
class Department:
    id: int (PK)
    name: str
    working_hours: str | None
    phone: str | None
    email: str | None
    room: str | None
    building_id: int (FK) | None
    notes: str | None

class Building:
    id: int (PK)
    name: str
    address: str
```

---

### 8. Группа (одногруппники)

#### API Endpoints
```
GET/POST/PUT/DELETE /api/classmates
POST /api/classmates/{id}/photo
```

#### Модель данных
```python
class Classmate:
    id: int (PK)
    last_name: str
    first_name: str
    middle_name: str | None
    phone: str | None
    telegram: str | None
    vk: str | None
    role: str | None                # "староста"
    photo_url: str | None
```

---

### 9. Файловое хранилище

#### Требования
- Загрузка файлов на сервер
- Категории: методичка, задачник, лекции, шпаргалки, прочее
- Привязка к предмету (опционально)
- Массовая загрузка
- Просмотр в браузере + скачивание
- Ограничение: 50 MB на файл

#### API Endpoints
```
GET    /api/files
POST   /api/files/upload
GET    /api/files/{id}
GET    /api/files/{id}/download
GET    /api/files/{id}/preview
DELETE /api/files/{id}
PUT    /api/files/{id}
```

#### Модель данных
```python
class File:
    id: int (PK)
    filename: str
    stored_filename: str
    mime_type: str
    size: int
    category: str
    subject_id: int (FK) | None
    uploaded_by: int (FK)
    created_at: datetime
```

---

### 10. Учебный план (семестры)

#### API Endpoints
```
GET/POST/PUT/DELETE /api/semesters
GET  /api/semesters/current
PUT  /api/semesters/{id}/set-current
```

#### Модель данных
```python
class Semester:
    id: int (PK)
    number: int
    year_start: int
    year_end: int
    is_current: bool
    start_date: date
    end_date: date
```

---

### 11. Календарь

#### API Endpoints
```
GET /api/calendar
GET /api/calendar/day/{date}
GET /api/calendar/week/{date}
GET /api/calendar/month/{year}/{month}
```

Агрегирует данные из ScheduleEntry, Work, Subject.

---

### 12. Уведомления (Push)

#### Требования
- Дедлайны: за 3 дня, за 1 день, в день
- Изменение расписания
- Утренняя сводка (8:00)

#### API Endpoints
```
POST   /api/notifications/subscribe
DELETE /api/notifications/unsubscribe
GET    /api/notifications/settings
PUT    /api/notifications/settings
```

#### Модель данных
```python
class PushSubscription:
    id: int (PK)
    user_id: int (FK)
    endpoint: str
    p256dh: str
    auth: str

class NotificationSettings:
    id: int (PK)
    user_id: int (FK, unique)
    deadline_3_days: bool
    deadline_1_day: bool
    deadline_same_day: bool
    schedule_changes: bool
    morning_summary: bool
    morning_summary_time: time
```

---

### 13. Парный режим

- Два пользователя видят **все** данные друг друга
- Редактировать можно только **своё** (WorkStatus, Attendance)
- Общие данные редактируют оба

---

### 14. Голосовой ввод

Web Speech API для диктовки текста в заметки.

---

### 15. Прогресс и визуализация

#### API Endpoints
```
GET /api/progress
GET /api/progress/subjects
GET /api/progress/semester
```

---

## Страницы приложения

```
/                           # Dashboard
/login, /register           # Аутентификация
/schedule                   # Расписание
/subjects, /subjects/:id    # Предметы
/works, /works/:id          # Работы
/calendar                   # Календарь
/teachers, /teachers/:id    # Преподаватели
/classmates                 # Одногруппники
/files                      # Файлы
/university                 # Информация об универе
/plan                       # Учебный план
/attendance                 # Посещаемость
/progress                   # Прогресс
/partner                    # Данные партнёра
/settings                   # Настройки
```

---

## MVP (Первая версия)

### Включено в MVP
- ✅ Аутентификация (2 пользователя)
- ✅ Расписание (парсинг + отображение)
- ✅ Предметы (CRUD)
- ✅ Работы (CRUD + статусы + дедлайны)
- ✅ Преподаватели (CRUD)
- ✅ Инфо об универе (CRUD)
- ✅ Одногруппники (CRUD)
- ✅ Dashboard
- ✅ PWA (manifest + service worker)
- ✅ Адаптив + тёмная тема
- ✅ Парный режим (просмотр)

### НЕ включено в MVP (Фаза 2+)
- ❌ Файлы
- ❌ Посещаемость
- ❌ Календарь
- ❌ Уведомления
- ❌ Прогресс
- ❌ Учебный план
- ❌ Голосовой ввод

---

## Планы на будущее

### Фаза 2
- Push-уведомления
- Файловое хранилище
- Посещаемость
- Календарь
- Прогресс-бары
- Учебный план

### Фаза 3
- Голосовой ввод
- История изменений
- Парсинг расписания преподавателя

### Фаза 4 (далёкое будущее)
- Виджеты для телефона
- Telegram-бот
- AI-агент для голосовых команд
- Автоматический расчёт автомата
- Google Calendar интеграция
- Расширение на других пользователей
- Доменное имя

---

## Деплой

### Требования к серверу
- Ubuntu 22.04+
- Docker + Docker Compose
- 2+ GB RAM
- 20+ GB SSD

### Команды
```bash
git clone <repo>
cd studyhelper
cp .env.example .env
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose exec backend alembic upgrade head
```

---

## Ссылки

- **Расписание ОмГУ:** https://eservice.omsu.ru/schedule/#/schedule/group/5028
- **Сайт ОмГУ:** https://omsu.ru
- **Брендбук ОмГУ:** https://drive.google.com/drive/folders/1jL1C79hmJPs__D-87IPIEiFjEAxSnZO2

---

## Чеклист для Claude Code

### Документация (СНАЧАЛА!)
- [ ] Создать структуру папок
- [ ] Заполнить `CLAUDE.md`
- [ ] Заполнить `Current_task.md` — "Инициализация проекта"
- [ ] Заполнить `Decisions.md` — архитектурные решения
- [ ] Заполнить `project_status.md` — статус (0%)
- [ ] Создать `plans/MVP_plan.md`
- [ ] Создать `plans/full_plan.md`
- [ ] Создать `plans/future_features.md`

### Инициализация проекта
- [ ] Создать `frontend/` (Vite + React + TypeScript)
- [ ] Создать `backend/` (FastAPI)
- [ ] Создать `docker-compose.yml`
- [ ] Создать `.env.example`
- [ ] Создать `docs/database_schema.md`

**Приоритет:** Сначала документация, потом код.
