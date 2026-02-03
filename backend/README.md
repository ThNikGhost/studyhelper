# StudyHelper Backend

FastAPI backend for StudyHelper PWA.

## Setup

```bash
# Install dependencies
uv sync

# Install dev dependencies
uv sync --extra dev

# Run development server
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest

# Run linter
uv run ruff check .
uv run ruff format .
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
