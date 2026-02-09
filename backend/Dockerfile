# === Builder stage ===
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini ./
COPY README.md ./

# Install the project itself
RUN uv sync --frozen --no-dev


# === Runtime stage ===
FROM python:3.12-slim

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/sh --create-home appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/src /app/src
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/alembic.ini

# Copy and fix entrypoint (Windows CRLF → Linux LF)
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Create upload directories
RUN mkdir -p /app/uploads/avatars /app/uploads/files && \
    chown -R appuser:appuser /app

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Healthcheck using stdlib (no curl/wget needed)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://localhost:8000/health')"

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
