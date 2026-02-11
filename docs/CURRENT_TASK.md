# Текущая задача

## Статус
**Завершена.** Снятие ограничения на 2 пользователей.

## Последняя сессия: Remove user limit — 2026-02-11

### Сделано
- [x] Удалена константа MAX_USERS=2 и проверка лимита в register_user()
- [x] Удалён класс UserLimitException
- [x] Удалён тест test_register_max_users_limit
- [x] Обновлены docstrings (убраны упоминания "2 users")
- [x] Удалён комментарий про 2 пользователей из RegisterPage
- [x] Обновлена документация (CLAUDE.md, project_status.md, fastapi.md)
- [x] Backend тесты: 15 passed (auth)
- [x] Frontend build: успешно

## Следующие задачи (приоритет)
1. **SSL (HTTPS)** — настроить Let's Encrypt (P0) — в работе параллельно
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
