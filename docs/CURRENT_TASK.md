# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: Code Review Final (P1-7, P1-8, P1-10) — 2026-02-14

### Сделано
Реализованы финальные пункты code review:

**P1-7: Structured Logging (structlog):**
1. Backend: `src/logging_config.py` — ProcessorFormatter перехватывает stdlib logging (0 изменений в 15+ модулях)
2. Backend: `src/middleware/request_id.py` — X-Request-ID header + ContextVar для per-request tracking
3. Backend: `src/main.py` — удалена старая setup_logging(), добавлены middleware
4. Backend: 8 тестов (JSON output, console output, log levels, stdlib interception, noisy loggers, request_id)
5. Backend: 3 теста RequestIdMiddleware (response header, incoming ID preserved, unique IDs)

**P1-8: Prometheus Metrics:**
6. Backend: `src/metrics.py` — Counter, Histogram, Gauge для HTTP и schedule sync
7. Backend: `src/middleware/prometheus.py` — auto-instrumentation с path normalization (`/\d+/` → `/{id}/`)
8. Backend: `src/main.py` — GET /metrics endpoint, PrometheusMiddleware, APP_INFO
9. Backend: `src/scheduler.py` — SCHEDULE_SYNC_TOTAL (success/skipped/error) + duration
10. `nginx/nginx.conf` — /metrics location (Docker internal networks only)
11. Backend: 12 тестов (endpoint, path normalization, counters, exclusions)

**P1-10: LK Parser тесты с respx:**
12. Backend: `tests/test_lk_parser.py` — полностью переписан с respx transport-level mocking
13. Удалены: MagicMock, patch, CI_SKIP — все 16 тестов работают в CI без пропусков

### Метрики
- Backend тестов: 466 passed (было 421, +45 новых)
- Frontend тестов: ~380 passed
- Линтер: ✅ Ruff + ESLint чисто
- Build: ✅ TypeScript + Vite

### Результат
- Structured logging: JSON output в production, colored console в dev, request_id tracking
- Prometheus: HTTP метрики, schedule sync метрики, /metrics endpoint (restricted to internal networks)
- LK parser тесты: 0 CI skips, transport-level mocking с respx

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

### Оставшиеся пункты Code Review (низкий приоритет):
- P2-11: Виртуализация в FilesPage — требует @tanstack/react-virtual

## Блокеры / Вопросы
Нет блокеров.
