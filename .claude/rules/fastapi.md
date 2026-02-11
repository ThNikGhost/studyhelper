---
globs: ["backend/src/**/*.py"]
description: FastAPI and SQLAlchemy patterns for backend
---

# FastAPI / SQLAlchemy Rules

## Module Structure
Each backend module follows: `model → schema → service → router`
```
backend/src/{module}/
├── models.py    # SQLAlchemy models
├── schemas.py   # Pydantic v2 schemas
├── service.py   # Business logic (async)
├── router.py    # FastAPI endpoints
└── exceptions.py # Module-specific exceptions (optional)
```

## Router Patterns
- Prefix: `/api/v1/{module}` (defined in `src/main.py`)
- Use `Depends()` for dependency injection (db session, current user)
- Return Pydantic schemas, not raw dicts
- HTTP exceptions: raise `HTTPException(status_code=..., detail=...)`
- Tags: one tag per module for OpenAPI grouping

```python
@router.get('/', response_model=list[ItemResponse])
async def list_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ItemResponse]:
    """List all items for the current user."""
    return await item_service.get_all(db, current_user.id)
```

## Service Layer
- All functions are `async`
- Accept `AsyncSession` as first parameter
- Raise custom exceptions (not HTTPException — that's for routers)
- Use `select()` + `await db.execute()` pattern
- Atomic updates: `db.add()` → `await db.flush()` → `await db.commit()`

## SQLAlchemy Models
- Use `Mapped[]` and `mapped_column()` (SQLAlchemy 2.0 style)
- Base class: `src.database.base.Base`
- Common mixins: `id`, `created_at`, `updated_at`
- Relationships: `relationship()` with `back_populates`

## Pydantic Schemas
- Pydantic v2 with `model_config = ConfigDict(from_attributes=True)`
- Separate schemas: `Create`, `Update`, `Response`
- `max_length` on string fields matching DB constraints
- `HttpUrl` for URL fields, validated

## Authentication
- JWT tokens: access (15min) + refresh (7 days)
- `get_current_user` dependency for protected routes
- Passwords: bcrypt via passlib

## Database
- PostgreSQL (production) / aiosqlite (tests)
- Alembic for migrations: `backend/alembic/`
- Always use parameterized queries (SQLAlchemy handles this)
