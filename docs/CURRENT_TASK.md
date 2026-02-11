# Текущая задача

## Статус
**Завершена.** Bugfixes (modal focus, PE filter, formatTimeUntil) + test-runner agent.

## Последняя сессия: Bugfixes + DX — 2026-02-11

### Сделано
- [x] Fix: Modal `useEffect` — фокус крался при ре-рендере. Исправлено: `onCloseRef` + зависимость только `[open]`
- [x] Feat: PE teacher filter (`lib/peTeacherFilter.ts`) — `isPeEntry`, `filterPeEntries`, localStorage, `PeTeacherSelect`
- [x] Fix: `formatTimeUntil` принимал секунды, backend отдаёт минуты — обновлены тесты, моки, SchedulePage
- [x] Fix: SchedulePage вручную делил `time_until_next / 60` — заменено на `formatTimeUntil()`
- [x] DX: `.claude/agents/test-runner.md` — агент для запуска тестов (Vitest на Windows зависает)
- [x] Деплой на сервер — nginx пересобран
- [x] 348 frontend тестов проходят (3 OOM при cleanup)
- [x] TypeScript, ESLint, build — чисто

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
