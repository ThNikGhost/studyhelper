# Текущая задача

## Статус
**Завершена.** Code review scheduler + все исправления применены.

## Последняя сессия: Scheduler Code Review Fixes — 2026-02-10

### Сделано
- [x] Code review всех незакоммиченных изменений (schedule auto-sync)
- [x] P1: Добавлен `jitter=60` в IntervalTrigger (разнос запусков между workers)
- [x] P1: Redis auto-reconnect в `_get_redis()` (ping healthcheck + recreate)
- [x] P2: `LockNotOwnedError` вместо bare `Exception` при release lock
- [x] P2: `misfire_grace_time=3600` на scheduler job
- [x] P2: `contextlib.suppress(Exception)` вместо try/except/pass (ruff SIM105)
- [x] P3: `.gitignore` — добавлены `nul`, `backend/test_output.txt`
- [x] P3: `.gitattributes` — `*.sh text eol=lf` для Docker совместимости
- [x] 4 новых теста: lock expired, redis create/reuse/reconnect
- [x] 348 тестов backend — все проходят
- [x] Ruff lint + format — чисто

### Не закоммичено
Все изменения (schedule auto-sync + code review fixes) требуют коммита и пуша.

## Следующие задачи (приоритет)
1. **SSL (HTTPS)** — настроить Let's Encrypt (P0, требует доменное имя)
2. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
3. **05-ics-export** — экспорт расписания в .ics (P2)
4. **02-push-notifications** — push-уведомления (P1)

## Деплой на сервер
После коммита — пересобрать и перезапустить контейнеры:
```bash
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d
```

## Блокеры / Вопросы
Нет блокеров.
