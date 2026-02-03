# Database Schema — StudyHelper

## Overview

База данных PostgreSQL с использованием SQLAlchemy 2.0 и asyncpg.

---

## ER Diagram (упрощённая)

```
┌─────────────┐       ┌─────────────┐
│   users     │       │  semesters  │
└─────────────┘       └─────────────┘
      │                     │
      │                     │
      ▼                     ▼
┌─────────────┐       ┌─────────────┐
│work_statuses│◄──────│  subjects   │
└─────────────┘       └─────────────┘
      │                     │
      │                     │
      ▼                     ▼
┌─────────────┐       ┌─────────────┐
│   works     │       │schedule_    │
└─────────────┘       │entries      │
                      └─────────────┘
                            │
                            ▼
                      ┌─────────────┐
                      │  teachers   │
                      └─────────────┘
```

---

## Tables

### users
Пользователи системы (максимум 2).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email |
| password_hash | VARCHAR(255) | NOT NULL | Хеш пароля |
| name | VARCHAR(100) | NOT NULL | Имя пользователя |
| avatar_url | VARCHAR(500) | NULL | URL аватара |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Дата создания |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Дата обновления |

---

### semesters
Семестры обучения.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| number | SMALLINT | NOT NULL | Номер семестра (1-12) |
| year_start | SMALLINT | NOT NULL | Год начала |
| year_end | SMALLINT | NOT NULL | Год окончания |
| is_current | BOOLEAN | NOT NULL, DEFAULT FALSE | Текущий семестр |
| start_date | DATE | NULL | Дата начала |
| end_date | DATE | NULL | Дата окончания |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

---

### subjects
Учебные предметы.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| name | VARCHAR(200) | NOT NULL | Название предмета |
| short_name | VARCHAR(50) | NULL | Сокращённое название |
| semester_id | INTEGER | FK → semesters.id, NOT NULL | Семестр |
| control_type | VARCHAR(20) | NOT NULL | exam/credit/diff_credit |
| grading_system | VARCHAR(20) | NOT NULL, DEFAULT 'standard' | standard/points |
| max_points | SMALLINT | NULL | Макс. баллов (если points) |
| auto_requirements | TEXT | NULL | Требования к автомату |
| notes | TEXT | NULL | Заметки |
| color | VARCHAR(7) | NULL | Цвет (#RRGGBB) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

**Indexes:** `semester_id`

---

### schedule_entries
Записи расписания.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| day_of_week | SMALLINT | NOT NULL | 0-6 (0=Пн) |
| week_type | VARCHAR(10) | NULL | odd/even/NULL |
| time_start | TIME | NOT NULL | Время начала |
| time_end | TIME | NOT NULL | Время окончания |
| subject_id | INTEGER | FK → subjects.id, NULL | Привязка к предмету |
| subject_name | VARCHAR(200) | NOT NULL | Название из парсинга |
| teacher_id | INTEGER | FK → teachers.id, NULL | Привязка к преподавателю |
| teacher_name | VARCHAR(200) | NULL | Имя из парсинга |
| room | VARCHAR(50) | NULL | Аудитория |
| entry_type | VARCHAR(20) | NOT NULL | lecture/practice/lab |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

**Indexes:** `day_of_week`, `subject_id`, `teacher_id`

---

### schedule_snapshots
Снапшоты расписания для отслеживания изменений.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| hash | VARCHAR(32) | NOT NULL | MD5 хеш данных |
| data | JSONB | NOT NULL | Полные данные расписания |
| parsed_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Время парсинга |

---

### teachers
Преподаватели.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| last_name | VARCHAR(100) | NOT NULL | Фамилия |
| first_name | VARCHAR(100) | NOT NULL | Имя |
| middle_name | VARCHAR(100) | NULL | Отчество |
| email | VARCHAR(255) | NULL | Email |
| phone | VARCHAR(20) | NULL | Телефон |
| telegram | VARCHAR(100) | NULL | Telegram username |
| vk | VARCHAR(200) | NULL | VK ссылка |
| room | VARCHAR(50) | NULL | Кабинет |
| schedule_url | VARCHAR(500) | NULL | Ссылка на расписание |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

---

### works
Учебные работы.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| subject_id | INTEGER | FK → subjects.id, NOT NULL | Предмет |
| title | VARCHAR(300) | NOT NULL | Название работы |
| description | TEXT | NULL | Описание |
| work_type | VARCHAR(20) | NOT NULL | homework/lab/test/etc |
| deadline | TIMESTAMP | NULL | Дедлайн |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'medium' | high/medium/low |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

**Indexes:** `subject_id`, `deadline`

---

### work_statuses
Статусы работ (отдельно для каждого пользователя).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| work_id | INTEGER | FK → works.id, NOT NULL | Работа |
| user_id | INTEGER | FK → users.id, NOT NULL | Пользователь |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'not_started' | not_started/in_progress/done |
| completed_at | TIMESTAMP | NULL | Время выполнения |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

**Unique:** `(work_id, user_id)`
**Indexes:** `work_id`, `user_id`, `status`

---

### work_status_history
История изменений статусов.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| work_status_id | INTEGER | FK → work_statuses.id, NOT NULL | Статус работы |
| old_status | VARCHAR(20) | NULL | Предыдущий статус |
| new_status | VARCHAR(20) | NOT NULL | Новый статус |
| changed_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Время изменения |

**Indexes:** `work_status_id`

---

### attendance (Фаза 2)
Посещаемость.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| user_id | INTEGER | FK → users.id, NOT NULL | Пользователь |
| schedule_entry_id | INTEGER | FK → schedule_entries.id, NOT NULL | Запись расписания |
| date | DATE | NOT NULL | Дата занятия |
| is_present | BOOLEAN | NOT NULL, DEFAULT TRUE | Присутствовал |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

**Unique:** `(user_id, schedule_entry_id, date)`

---

### departments
Подразделения университета.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| name | VARCHAR(300) | NOT NULL | Название |
| working_hours | VARCHAR(100) | NULL | Часы работы |
| phone | VARCHAR(20) | NULL | Телефон |
| email | VARCHAR(255) | NULL | Email |
| room | VARCHAR(50) | NULL | Кабинет |
| building_id | INTEGER | FK → buildings.id, NULL | Корпус |
| notes | TEXT | NULL | Заметки |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

---

### buildings
Корпуса университета.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| name | VARCHAR(200) | NOT NULL | Название |
| address | VARCHAR(300) | NOT NULL | Адрес |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

---

### classmates
Одногруппники.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| last_name | VARCHAR(100) | NOT NULL | Фамилия |
| first_name | VARCHAR(100) | NOT NULL | Имя |
| middle_name | VARCHAR(100) | NULL | Отчество |
| phone | VARCHAR(20) | NULL | Телефон |
| telegram | VARCHAR(100) | NULL | Telegram |
| vk | VARCHAR(200) | NULL | VK |
| role | VARCHAR(50) | NULL | Роль (староста и т.д.) |
| photo_url | VARCHAR(500) | NULL | URL фото |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

---

### files (Фаза 2)
Загруженные файлы.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| filename | VARCHAR(255) | NOT NULL | Оригинальное имя |
| stored_filename | VARCHAR(255) | NOT NULL | Имя на диске |
| mime_type | VARCHAR(100) | NOT NULL | MIME тип |
| size | INTEGER | NOT NULL | Размер в байтах |
| category | VARCHAR(50) | NOT NULL | Категория |
| subject_id | INTEGER | FK → subjects.id, NULL | Предмет |
| uploaded_by | INTEGER | FK → users.id, NOT NULL | Загрузивший |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

**Indexes:** `subject_id`, `category`, `uploaded_by`

---

### push_subscriptions (Фаза 2)
Подписки на push-уведомления.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| user_id | INTEGER | FK → users.id, NOT NULL | Пользователь |
| endpoint | TEXT | NOT NULL | Push endpoint |
| p256dh | VARCHAR(255) | NOT NULL | Public key |
| auth | VARCHAR(255) | NOT NULL | Auth secret |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

---

### notification_settings (Фаза 2)
Настройки уведомлений.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Primary key |
| user_id | INTEGER | FK → users.id, UNIQUE, NOT NULL | Пользователь |
| deadline_3_days | BOOLEAN | NOT NULL, DEFAULT TRUE | За 3 дня |
| deadline_1_day | BOOLEAN | NOT NULL, DEFAULT TRUE | За 1 день |
| deadline_same_day | BOOLEAN | NOT NULL, DEFAULT TRUE | В день |
| schedule_changes | BOOLEAN | NOT NULL, DEFAULT TRUE | Изменения расписания |
| morning_summary | BOOLEAN | NOT NULL, DEFAULT TRUE | Утренняя сводка |
| morning_summary_time | TIME | NOT NULL, DEFAULT '08:00' | Время сводки |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | — |

---

## Migrations

Используем Alembic для миграций.

```bash
# Создание миграции
uv run alembic revision --autogenerate -m "description"

# Применение миграций
uv run alembic upgrade head

# Откат последней миграции
uv run alembic downgrade -1
```
