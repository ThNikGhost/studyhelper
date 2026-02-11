# Текущая задача

## Статус
**Завершена.** Code Review implementation (13 fixes) + deploy.

## Последняя сессия: Code Review — 2026-02-11

### Сделано
- [x] P0-1: CASCADE DELETE → SET NULL (absences + lesson_notes FK), миграция f1a2b3c4d5e6
- [x] P0-2: Убран StaticFiles mount /uploads + nginx location
- [x] P0-3: Content-Disposition header injection fix (urllib.parse.quote)
- [x] P0-4: LIKE wildcard injection fix (escape %, _, \)
- [x] P1-1: AbortSignal в NoteEditor API calls
- [x] P1-2: schedule_group_id в Settings
- [x] P1-3: Redis authentication (--requirepass)
- [x] P1-4: Health endpoint проверяет DB + Redis
- [x] P2-1: DRY magic bytes
- [x] P2-2: Удалён aiopg
- [x] P2-3: python-jose → PyJWT
- [x] P2-4: void peTeacher → явный параметр
- [x] P2-5: Пагинация limit/offset (files, notes)
- [x] Hotfix: alembic env.py psycopg2 → psycopg
- [x] REDIS_PASSWORD добавлен на сервере
- [x] Деплой — 15 миграций, все контейнеры healthy, health: db=true redis=true
- [x] Backend: 353 тестов, Frontend: 348 тестов — всё зелёное

## Следующие задачи (приоритет)
1. **SSL (HTTPS)** — настроить Let's Encrypt (P0, требует доменное имя)
2. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
3. **05-ics-export** — экспорт расписания в .ics (P2)
4. **02-push-notifications** — push-уведомления (P1)

## Деплой на сервер
```bash
cd /opt/repos/studyhelper
git pull origin main
docker compose -f docker-compose.prod.yml build backend nginx
docker compose -f docker-compose.prod.yml up -d
```

## Блокеры / Вопросы
Нет блокеров.
