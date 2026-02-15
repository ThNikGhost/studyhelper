#!/bin/bash
# PostgreSQL restore script for StudyHelper
# Restores database from a .sql.gz backup file
# Usage: ./restore.sh [backup_file.sql.gz]
set -euo pipefail

COMPOSE_DIR="/opt/repos/studyhelper"
BACKUP_DIR="${COMPOSE_DIR}/backups"

# Show available backups if no argument provided
if [ -z "${1:-}" ]; then
  echo "Usage: $0 <backup_file.sql.gz>"
  echo ""
  echo "Available backups:"
  if ls "${BACKUP_DIR}"/studyhelper_*.sql.gz 1>/dev/null 2>&1; then
    ls -lh "${BACKUP_DIR}"/studyhelper_*.sql.gz
  else
    echo "  (none)"
  fi
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERROR: File not found: $BACKUP_FILE"
  exit 1
fi

if [[ ! "$BACKUP_FILE" =~ \.sql\.gz$ ]]; then
  echo "ERROR: File must be a .sql.gz backup"
  exit 1
fi

# Validate gzip integrity
if ! gunzip -t "$BACKUP_FILE" 2>/dev/null; then
  echo "ERROR: Backup file is corrupted"
  exit 1
fi

# Load database credentials from .env
if [ ! -f "${COMPOSE_DIR}/.env" ]; then
  echo "ERROR: .env file not found at ${COMPOSE_DIR}/.env"
  exit 1
fi
source "${COMPOSE_DIR}/.env"

if [ -z "${POSTGRES_USER:-}" ] || [ -z "${POSTGRES_DB:-}" ]; then
  echo "ERROR: POSTGRES_USER or POSTGRES_DB not set in .env"
  exit 1
fi

SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "WARNING: This will REPLACE the current database with:"
echo "  File: $BACKUP_FILE ($SIZE)"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo "Restoring database..."
cd "$COMPOSE_DIR"

# Verify db container is running
if ! docker compose -f docker-compose.prod.yml ps db --format '{{.State}}' | grep -q "running"; then
  echo "ERROR: db container is not running"
  exit 1
fi
gunzip -c "$BACKUP_FILE" \
  | docker compose -f docker-compose.prod.yml exec -T db \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "Database restored from: $BACKUP_FILE"
