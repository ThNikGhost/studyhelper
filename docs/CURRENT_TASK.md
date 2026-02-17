# Текущая задача

## Статус
**Проект в режиме поддержки. Code review fixes завершены.**

## Последняя сессия: Code Review Fix (SEC-1 follow-up) — 2026-02-17

### Сделано
- **`backend/src/main.py`** — /metrics: `import ipaddress` на уровне модуля, `_METRICS_ALLOWED_NETWORKS` константа (добавлена `192.168.0.0/16`), fallback `403` при отсутствии `client_ip`
- **`docker-compose.prod.yml`** — Redis healthcheck: `REDISCLI_AUTH=$REDIS_PASSWORD` вместо `-a` (подавляет password warning в логах)
- **`scripts/backup.sh`** — GPG passphrase через `--passphrase-fd 0` вместо `--passphrase` CLI arg (скрыт от `ps aux`)
- **`backend/src/routers/auth.py`** — комментарий `# Must match UserSettingsUpdate schema fields` над `allowed_fields`
- **`docker-compose.yml`** — комментарий `# Requires POSTGRES_PASSWORD in .env` к db-сервису
- **`.env.example`** — обновлён: добавлены `REDIS_PASSWORD`, `SENTRY_DSN`, `TELEGRAM_*`, `BACKUP_ENCRYPTION_KEY`

### Верификация
- Backend тесты: 619 passed
- Ruff check + format: clean
- ESLint: clean

## Следующие шаги (по приоритету)
- Закоммитить и запушить все изменения (SEC-1 + code review fixes + uv.lock)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)
- (Будущее) Release signing: keystore + GitHub Secrets для signed APK

## Блокеры / Вопросы
- Нет
