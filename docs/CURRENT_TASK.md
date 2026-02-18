# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован.**

## Последняя сессия: CD Continuous Deployment — 2026-02-18

### Сделано
- **`.github/workflows/ci.yml`** — добавлен `deploy` job: SSH setup через `printf`, `ssh prod deploy.sh`, health check 10 попыток, auto-rollback при падении health check
- **`scripts/deploy.sh`** — git pull + docker compose build --pull + up --remove-orphans + image prune, сохраняет PREVIOUS_SHA в `/tmp/deploy_state`
- **`scripts/rollback.sh`** — git reset --hard PREVIOUS_SHA + rebuild из сохранённого state
- Оба скрипта с executable bit (`100755`) в git index

### Ручные шаги (одноразово, перед активацией)
1. Сгенерировать SSH deploy key: `ssh-keygen -t ed25519 -C "github-actions-deploy" -f deploy_key -N ""`
2. Добавить публичный ключ на сервер (`deploy@89.110.93.63`): `cat deploy_key.pub >> ~/.ssh/authorized_keys`
3. Добавить 3 GitHub Secrets:
   - `DEPLOY_SSH_KEY` — содержимое `deploy_key` (приватный ключ)
   - `DEPLOY_SSH_HOST` — `89.110.93.63`
   - `DEPLOY_SSH_KNOWN_HOSTS` — вывод `ssh-keyscan -H 89.110.93.63`
4. Bootstrapping на сервере: `cd /opt/repos/studyhelper && git pull origin main`

## Следующие шаги (по приоритету)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
