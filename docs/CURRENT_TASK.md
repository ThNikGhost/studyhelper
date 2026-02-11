# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: LK Parser implementation — 2026-02-12

### Сделано
1. Модели: `LkCredentials`, `SessionGrade`, `SemesterDiscipline` (src/models/lk.py)
2. Схемы Pydantic v2: credentials, status, grades, disciplines (src/schemas/lk.py)
3. Crypto helper: Fernet encryption с PBKDF2HMAC (src/utils/crypto.py)
4. LK Parser: HTTP клиент с OAuth2 авторизацией (src/parser/lk_parser.py)
5. Сервис: credentials CRUD, verify, sync, upsert (src/services/lk.py)
6. Роутер: `/api/v1/lk/*` endpoints (src/routers/lk.py)
7. Alembic миграция: `2a3b4c5d6e7f_add_lk_tables`
8. Тесты: 51 тест (crypto: 6, API: 29, parser: 16)

### API Endpoints
- `GET /api/v1/lk/status` — статус подключения ЛК
- `POST /api/v1/lk/credentials` — сохранить credentials (encrypted)
- `DELETE /api/v1/lk/credentials` — удалить credentials
- `POST /api/v1/lk/verify` — проверить credentials без сохранения
- `POST /api/v1/lk/sync` — синхронизировать оценки и дисциплины
- `GET /api/v1/lk/grades` — получить оценки (filter: session)
- `GET /api/v1/lk/grades/sessions` — список сессий
- `GET /api/v1/lk/disciplines` — получить дисциплины (filter: semester)
- `GET /api/v1/lk/disciplines/semesters` — список семестров

### Результат
- **418 тестов backend** — все проходят
- Линтер чистый (ruff check + format)
- Готово для деплоя и frontend интеграции

## Следующие задачи (приоритет)
1. **Frontend: LK интеграция** — страница настроек ЛК, отображение оценок
2. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
3. **05-ics-export** — экспорт расписания в .ics (P2)
4. **02-push-notifications** — push-уведомления (P1)

## Блокеры / Вопросы
Нет блокеров.
