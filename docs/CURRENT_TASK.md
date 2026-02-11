# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: UI improvements — 2026-02-11

### Сделано
1. **ClassmatesPage** — добавлены: название группы (МБС-301-О-01), счётчик общий и по подгруппам
2. **SemestersPage** — показывается только номер семестра вместо полного названия
3. **DashboardPage** — убрана фраза "Что будем делать сегодня?"
4. **formatLocation** — утилита для парсинга формата API:
   - `"(6"` → `"6"` (убирает скобки)
   - `"113) Спортивный зал"` → `"113"` (извлекает номер)
   - Результат: `"6-113"`
5. **nginx** — location `/uploads/avatars/` для публичных аватарок

### Коммиты
- `d796e02` — fix(ui): improve classmates page and dashboard display
- `f3a408e` — fix(ui): filter out gym room names from location display
- `24aae5a` — fix(ui): extract room number from gym location strings

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

## Деплой на сервер
```bash
cd /opt/repos/studyhelper
git pull origin main
docker compose -f docker-compose.prod.yml build nginx
docker compose -f docker-compose.prod.yml up -d nginx
```

## Блокеры / Вопросы
Нет блокеров.
