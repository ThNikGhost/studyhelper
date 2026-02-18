#!/bin/bash
# Rollback script: revert to previous commit and rebuild.
# Called by GitHub Actions CD workflow on health check failure.
# Can also be run manually on the server.

set -euo pipefail

REPO_DIR="/opt/repos/studyhelper"
COMPOSE_FILE="docker-compose.prod.yml"
STATE_FILE="/tmp/deploy_state"

cd "$REPO_DIR"

if [ ! -f "$STATE_FILE" ]; then
    echo "No deploy state found at $STATE_FILE, cannot rollback" >&2
    exit 1
fi

# shellcheck source=/dev/null
source "$STATE_FILE"
echo "Rolling back to: $PREVIOUS_SHA"

# Reset to previous commit (stays on main branch, unlike git checkout)
git reset --hard "$PREVIOUS_SHA"

docker compose -f "$COMPOSE_FILE" build
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

rm -f "$STATE_FILE"
echo "Rollback to $PREVIOUS_SHA completed"
