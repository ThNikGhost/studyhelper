# Текущая задача

## Статус
**Аудит безопасности (Фаза 1+2) завершён. Проект в режиме поддержки.**

## Последняя сессия: Security Audit Phase 1+2 — 2026-02-17

### Сделано (Фаза 1 — Quick wins)
- **Rate limit** `/auth/refresh` — `@limiter.limit("10/minute")`
- **Telegram webhook** — strict secret validation (always required when bot token set)
- **Config validator** — SECRET_KEY ≥32 chars in prod, TELEGRAM_WEBHOOK_SECRET required with bot token
- **Redis healthcheck** — authenticated with `$REDIS_PASSWORD`
- **File deletion** — ownership check (`uploaded_by != current_user.id → 403`)
- **VK URL sanitization** — `sanitizeUrl()` allows only http/https protocols
- **Mass-assignment** — explicit `allowed_fields` whitelist in PATCH settings
- **Permissions-Policy** header — `camera=(), microphone=(), geolocation=(), payment=()`
- **server_tokens off** — hide nginx version
- **CI permissions** — `permissions: contents: read` in ci.yml
- **/metrics** — app-level IP check (defense-in-depth)

### Сделано (Фаза 2 — Supply chain + hardening)
- **SHA-pinning** — all GitHub Actions pinned to commit SHA (ci.yml + android.yml)
- **Docker uv** — pinned to v0.10.3 (was `:latest`)
- **Docker certbot** — pinned to v4.1.0 (was `:latest`)
- **Backup encryption** — optional gpg symmetric AES-256 (BACKUP_ENCRYPTION_KEY env)
- **passlib removed** — dead dependency, bcrypt used directly
- **LkSyncError** — generic error messages, no exception detail leaks
- **dev-compose** — removed `POSTGRES_HOST_AUTH_METHOD: trust`, bound ports to 127.0.0.1

### Файлы изменены
- `backend/src/routers/auth.py` — rate limit + explicit field assignment
- `backend/src/routers/files.py` — ownership check
- `backend/src/routers/telegram.py` — strict secret check
- `backend/src/config.py` — validators (SECRET_KEY min length, telegram secret)
- `backend/src/main.py` — /metrics IP check
- `backend/src/services/lk.py` — generic error messages
- `backend/pyproject.toml` — passlib → bcrypt
- `backend/uv.lock` — updated
- `backend/Dockerfile` — uv pinned
- `frontend/src/pages/ClassmatesPage.tsx` — sanitizeUrl()
- `nginx/nginx.conf` — server_tokens off, Permissions-Policy
- `docker-compose.prod.yml` — Redis healthcheck, certbot pinned
- `docker-compose.yml` — removed trust, 127.0.0.1 ports
- `.github/workflows/ci.yml` — permissions + SHA-pinning
- `.github/workflows/android.yml` — SHA-pinning
- `scripts/backup.sh` — gpg encryption + .gpg rotation

## Следующие шаги (по приоритету)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)
- (Будущее) Release signing: keystore + GitHub Secrets для signed APK

## Блокеры / Вопросы
- Нет
