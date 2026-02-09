#!/bin/sh
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
retries=0
max_retries=30
until python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('db', 5432))
    s.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null; do
    retries=$((retries + 1))
    if [ "$retries" -ge "$max_retries" ]; then
        echo "ERROR: PostgreSQL not available after $max_retries retries"
        exit 1
    fi
    echo "PostgreSQL not ready (attempt $retries/$max_retries), waiting 2s..."
    sleep 2
done
echo "PostgreSQL is ready!"

# Run database migrations
echo "Running Alembic migrations..."
alembic upgrade head
echo "Migrations complete!"

# Start the application
echo "Starting uvicorn..."
exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --proxy-headers \
    --forwarded-allow-ips='*' \
    --log-level info
