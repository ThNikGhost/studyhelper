# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: Attendance Logic Rewrite — 2026-02-11

### Сделано
Полная переработка логики посещаемости:

1. **Backend**:
   - `planned_classes` в модели Subject для учёта запланированных пар
   - Attendance сервис фильтрует по семестру (start_date/end_date)
   - Только завершённые пары показываются (lesson_date < today OR end_time <= now)
   - Новые поля: `total_planned`, `total_completed` в AttendanceStats
   - Все endpoints требуют `semester_id`
   - 29 тестов (было 22)

2. **Frontend**:
   - AttendancePage с dropdown выбора семестра
   - Предупреждение если у семестра нет дат
   - AttendanceStatsCard: "X из Y" формат (attended / total_planned)
   - SubjectsPage: поле planned_classes в форме
   - 357 тестов проходят

### Коммит
- `754f3e4` — feat(attendance): rewrite attendance logic with semester filtering

### Деплой
- Миграция `1f580bc1b2b5` применена
- Все 5 контейнеров healthy
- https://studyhelper1.ru работает

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

## Деплой на сервер
```bash
cd /opt/repos/studyhelper
git pull origin main
docker compose -f docker-compose.prod.yml build backend nginx
docker compose -f docker-compose.prod.yml up -d backend nginx
```

## Блокеры / Вопросы
Нет блокеров.
