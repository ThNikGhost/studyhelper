#!/bin/bash
# PostgreSQL backup script for StudyHelper
# Runs via host cron, dumps DB through Docker container
# Usage: ./backup.sh
# Cron:  0 3 * * * /opt/studyhelper/scripts/backup.sh >> /var/log/studyhelper-backup.log 2>&1
set -euo pipefail

COMPOSE_DIR="/opt/studyhelper"
BACKUP_DIR="${COMPOSE_DIR}/backups"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/studyhelper_${TIMESTAMP}.sql.gz"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting backup..."

# Load database credentials from .env
if [ ! -f "${COMPOSE_DIR}/.env" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: .env file not found at ${COMPOSE_DIR}/.env"
  exit 1
fi
source "${COMPOSE_DIR}/.env"

if [ -z "${POSTGRES_USER:-}" ] || [ -z "${POSTGRES_DB:-}" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: POSTGRES_USER or POSTGRES_DB not set in .env"
  exit 1
fi

mkdir -p "$BACKUP_DIR"

# Dump database through Docker container
cd "$COMPOSE_DIR"
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  | gzip > "$BACKUP_FILE"

# Verify backup is not empty
if [ ! -s "$BACKUP_FILE" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Backup file is empty: $BACKUP_FILE"
  rm -f "$BACKUP_FILE"
  exit 1
fi

SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup created: $BACKUP_FILE ($SIZE)"

# Rotate old backups
DELETED=$(find "$BACKUP_DIR" -name "studyhelper_*.sql.gz" -mtime +${RETENTION_DAYS} -delete -print | wc -l)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Rotated ${DELETED} backup(s) older than ${RETENTION_DAYS} days"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup completed successfully"
