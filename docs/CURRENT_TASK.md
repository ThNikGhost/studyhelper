# Текущая задача

## Статус
**Завершена.** SSL (HTTPS) настроен и задеплоен.

## Последняя сессия: SSL (HTTPS) — 2026-02-11

### Сделано
- [x] nginx/nginx.conf — 3 server-блока (HTTP redirect, HTTPS www redirect, HTTPS main)
- [x] nginx/nginx.conf — SSL, http2, HSTS, security headers в nested locations
- [x] nginx/Dockerfile — EXPOSE 443, HTTPS healthcheck
- [x] docker-compose.prod.yml — порт 443, certbot сервис, certbot volumes
- [x] .env.production.example — DOMAIN, CERTBOT_EMAIL, HTTPS_PORT, REDIS_PASSWORD
- [x] scripts/init-letsencrypt.sh — bootstrap скрипт (self-signed → real cert)
- [x] Деплой: сертификат получен (expires 2026-05-12), 5 контейнеров работают
- [x] Верификация: HTTPS 200, HTTP 301, www 301, HSTS, CSP, health OK

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

## Деплой на сервер
```bash
cd /opt/repos/studyhelper
git pull origin main
docker compose -f docker-compose.prod.yml build nginx
docker compose -f docker-compose.prod.yml up -d
```

## Блокеры / Вопросы
Нет блокеров.
