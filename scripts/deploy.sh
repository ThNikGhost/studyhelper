#!/bin/bash
# Deploy script: pull latest code and rebuild Docker containers.
# Called by GitHub Actions CD workflow after successful CI.
# Can also be run manually on the server.

set -euo pipefail

REPO_DIR="/opt/repos/studyhelper"
COMPOSE_FILE="docker-compose.prod.yml"

cd "$REPO_DIR"

# Save current commit for potential rollback
PREVIOUS_SHA=$(git rev-parse HEAD)
echo "Current SHA: $PREVIOUS_SHA"

# Pull latest code
git pull origin main
echo "New SHA: $(git rev-parse HEAD)"

# Rebuild images (--pull refreshes base images like node:22, python:3.12-slim)
docker compose -f "$COMPOSE_FILE" build --pull

# Roll out new containers
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

# Remove dangling images to free disk space on VPS
docker image prune -f

# Persist state for rollback
echo "PREVIOUS_SHA=$PREVIOUS_SHA" > /tmp/deploy_state
echo "Deploy completed successfully"
