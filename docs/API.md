# API Documentation — StudyHelper

## Base URL
```
Development: http://localhost:8000/api/v1
Production:  https://[domain]/api/v1
```

## Authentication
Все защищённые эндпоинты требуют заголовок:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Auth

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Регистрация пользователя | No |
| POST | `/auth/login` | Вход в систему | No |
| POST | `/auth/refresh` | Обновление access token | No* |
| POST | `/auth/logout` | Выход из системы | Yes |
| GET | `/auth/me` | Текущий пользователь | Yes |

*Требует refresh token в теле запроса

---

### Schedule

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/schedule` | Расписание на неделю | Yes |
| GET | `/schedule/today` | Расписание на сегодня | Yes |
| GET | `/schedule/current` | Текущая/следующая пара | Yes |
| POST | `/schedule/refresh` | Принудительное обновление | Yes |

---

### Subjects

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/subjects` | Список предметов | Yes |
| POST | `/subjects` | Создать предмет | Yes |
| GET | `/subjects/{id}` | Получить предмет | Yes |
| PUT | `/subjects/{id}` | Обновить предмет | Yes |
| DELETE | `/subjects/{id}` | Удалить предмет | Yes |
| GET | `/subjects/{id}/progress` | Прогресс по предмету | Yes |
| GET | `/subjects/{id}/works` | Работы по предмету | Yes |
| GET | `/subjects/{id}/files` | Файлы по предмету | Yes |

---

### Works

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/works` | Список работ | Yes |
| POST | `/works` | Создать работу | Yes |
| GET | `/works/{id}` | Получить работу | Yes |
| PUT | `/works/{id}` | Обновить работу | Yes |
| DELETE | `/works/{id}` | Удалить работу | Yes |
| PUT | `/works/{id}/status` | Изменить статус (для текущего пользователя) | Yes |
| GET | `/works/{id}/history` | История изменений статуса | Yes |
| GET | `/works/upcoming` | Ближайшие дедлайны | Yes |

---

### Teachers

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/teachers` | Список преподавателей | Yes |
| POST | `/teachers` | Создать преподавателя | Yes |
| GET | `/teachers/{id}` | Получить преподавателя | Yes |
| PUT | `/teachers/{id}` | Обновить преподавателя | Yes |
| DELETE | `/teachers/{id}` | Удалить преподавателя | Yes |

---

### University

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/university/departments` | Список подразделений | Yes |
| POST | `/university/departments` | Создать подразделение | Yes |
| GET | `/university/departments/{id}` | Получить подразделение | Yes |
| PUT | `/university/departments/{id}` | Обновить подразделение | Yes |
| DELETE | `/university/departments/{id}` | Удалить подразделение | Yes |
| GET | `/university/buildings` | Список корпусов | Yes |
| POST | `/university/buildings` | Создать корпус | Yes |
| PUT | `/university/buildings/{id}` | Обновить корпус | Yes |
| DELETE | `/university/buildings/{id}` | Удалить корпус | Yes |

---

### Classmates

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/classmates` | Список одногруппников | Yes |
| POST | `/classmates` | Создать одногруппника | Yes |
| GET | `/classmates/{id}` | Получить одногруппника | Yes |
| PUT | `/classmates/{id}` | Обновить одногруппника | Yes |
| DELETE | `/classmates/{id}` | Удалить одногруппника | Yes |
| POST | `/classmates/{id}/photo` | Загрузить фото | Yes |

---

### Semesters

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/semesters` | Список семестров | Yes |
| POST | `/semesters` | Создать семестр | Yes |
| GET | `/semesters/current` | Текущий семестр | Yes |
| PUT | `/semesters/{id}` | Обновить семестр | Yes |
| DELETE | `/semesters/{id}` | Удалить семестр | Yes |
| PUT | `/semesters/{id}/set-current` | Установить как текущий | Yes |

---

## Фаза 2+ (не в MVP)

### Files

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/files` | Список файлов | Yes |
| POST | `/files/upload` | Загрузить файл | Yes |
| GET | `/files/{id}` | Информация о файле | Yes |
| GET | `/files/{id}/download` | Скачать файл | Yes |
| GET | `/files/{id}/preview` | Просмотр файла | Yes |
| DELETE | `/files/{id}` | Удалить файл | Yes |
| PUT | `/files/{id}` | Обновить метаданные | Yes |

### Attendance

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/attendance` | Посещаемость | Yes |
| POST | `/attendance/mark-absent` | Отметить пропуск | Yes |
| POST | `/attendance/mark-present` | Отменить пропуск | Yes |
| GET | `/attendance/stats` | Общая статистика | Yes |
| GET | `/attendance/stats/{subject_id}` | Статистика по предмету | Yes |

### Calendar

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/calendar` | Общий календарь | Yes |
| GET | `/calendar/day/{date}` | События на день | Yes |
| GET | `/calendar/week/{date}` | События на неделю | Yes |
| GET | `/calendar/month/{year}/{month}` | События на месяц | Yes |

### Notifications

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/notifications/subscribe` | Подписаться на push | Yes |
| DELETE | `/notifications/unsubscribe` | Отписаться от push | Yes |
| GET | `/notifications/settings` | Настройки уведомлений | Yes |
| PUT | `/notifications/settings` | Обновить настройки | Yes |

### Progress

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/progress` | Общий прогресс | Yes |
| GET | `/progress/subjects` | Прогресс по предметам | Yes |
| GET | `/progress/semester` | Прогресс семестра | Yes |

---

## Response Format

### Success
```json
{
  "data": { ... },
  "message": "Success"
}
```

### Error
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

### Pagination
```json
{
  "data": [ ... ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |
