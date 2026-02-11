# Текущая задача

## Статус
**Завершена.** Notes per-subject refactor + cache invalidation fix + deploy.

## Последняя сессия: Notes per-subject — 2026-02-11

### Сделано
- [x] Backend: UNIQUE constraint (user_id, subject_name) вместо (user_id, schedule_entry_id)
- [x] Backend: Alembic миграция e8f9a0b1c2d3 с дедупликацией (DISTINCT ON)
- [x] Backend: create_note() → upsert (201 new / 200 updated)
- [x] Backend: GET /api/v1/notes/subject/{subject_name}
- [x] Backend: 353 тестов проходят (26 для notes)
- [x] Frontend: getNoteForSubject(), LessonDetailModal query по subject_name
- [x] Frontend: cache invalidation через queryClient.invalidateQueries
- [x] Frontend: noteSubjectNames Set вместо noteEntryIds
- [x] Frontend: 348 тестов проходят (CI зелёный)
- [x] Fix: `.env` симлинк на сервере (.env → .env.production)
- [x] Деплой на сервер — миграция применена, все контейнеры healthy

## Следующие задачи (приоритет)
1. **SSL (HTTPS)** — настроить Let's Encrypt (P0, требует доменное имя)
2. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
3. **05-ics-export** — экспорт расписания в .ics (P2)
4. **02-push-notifications** — push-уведомления (P1)

## Деплой на сервер
Backend + frontend изменения:
```bash
cd /opt/repos/studyhelper
git pull origin main
docker compose -f docker-compose.prod.yml build backend nginx
docker compose -f docker-compose.prod.yml up -d backend  # Миграция через entrypoint.sh
docker compose -f docker-compose.prod.yml up -d nginx     # Новый фронтенд
```

## Блокеры / Вопросы
Нет блокеров.
