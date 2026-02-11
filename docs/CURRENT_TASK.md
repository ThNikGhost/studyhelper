# Текущая задача

## Статус
**Завершена.** Bugfix: modal focus + PE teacher filter.

## Последняя сессия: Modal Focus Fix + PE Teacher Filter — 2026-02-11

### Сделано
- [x] Fix: Modal `useEffect` зависел от `[open, onClose]` → фокус крался при каждом ре-рендере. Исправлено: `onCloseRef` + зависимость только `[open]`
- [x] Feat: PE teacher filter utility (`lib/peTeacherFilter.ts`) — `isPeEntry`, `filterPeEntries`, `filterDaySchedule`, `filterWeekSchedule`, localStorage persistence
- [x] Feat: `PeTeacherSelect` dropdown component — выбор преподавателя физры
- [x] Интеграция в `SchedulePage` (фильтрация weekSchedule, кнопка в header)
- [x] Интеграция в `DashboardPage` (фильтрация todaySchedule для TodayScheduleWidget)
- [x] TypeScript, ESLint — чисто
- [x] 348 frontend тестов — все проходят (3 пропущены из-за Vitest OOM на Windows)
- [x] Build — чисто
- [x] Коммит `edbe5c3` запушен

## Следующие задачи (приоритет)
1. **SSL (HTTPS)** — настроить Let's Encrypt (P0, требует доменное имя)
2. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
3. **05-ics-export** — экспорт расписания в .ics (P2)
4. **02-push-notifications** — push-уведомления (P1)

## Деплой на сервер
Фронтенд-only изменения — пересобрать nginx:
```bash
docker compose -f docker-compose.prod.yml build nginx
docker compose -f docker-compose.prod.yml up -d nginx
```

## Блокеры / Вопросы
Нет блокеров.
