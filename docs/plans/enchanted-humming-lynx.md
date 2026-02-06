# План: Code Review — CI + все исправления

## Стратегическое решение

**Отложить на отдельный PR**: переход с localStorage на httpOnly cookies (#2) и механизм отзыва JWT (#17). Это масштабная переделка всей auth-системы (backend endpoints + frontend store + 264 теста), которую лучше делать отдельно.

**Docker/деплой**: не включаем, по запросу пользователя.

Итого: **~70 фиксов** в 7 фазах.

---

## Фаза 0: GitHub Actions CI

**Новый файл**: `.github/workflows/ci.yml`

Два параллельных job-а:
- **backend**: checkout → setup-python 3.12 → setup-uv → `uv sync --dev` → `ruff check .` → `ruff format --check .` → `pytest --cov=src --cov-report=term-missing -q`
- **frontend**: checkout → setup-node 20 → `npm ci` → `npm run lint` → `npm run build`

Триггеры: push и PR в `main`.

---

## Фаза 1: Backend Security

### 1.1 Валидация secret_key при запуске
- **Файл**: `backend/src/config.py`
- Добавить `model_validator`: если `debug=False` и `secret_key == "change-me-in-production"` → `ValueError`

### 1.2 Сузить CORS
- **Файл**: `backend/src/main.py:51-56`
- `allow_methods=["GET","POST","PUT","DELETE","OPTIONS"]`
- `allow_headers=["Authorization","Content-Type"]`

### 1.3 Rate limiting на auth
- Добавить `slowapi` в зависимости (`pyproject.toml`)
- **Новый файл**: `backend/src/utils/rate_limit.py` — `Limiter(key_func=get_remote_address)`
- **Файл**: `backend/src/main.py` — подключить limiter к app
- **Файл**: `backend/src/routers/auth.py` — `@limiter.limit("5/minute")` на login, `@limiter.limit("3/minute")` на register

### 1.4 Security headers middleware
- **Файл**: `backend/src/main.py`
- Новый `SecurityHeadersMiddleware`: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`

### 1.5 Глобальный exception handler
- **Файл**: `backend/src/main.py`
- `@app.exception_handler(Exception)` → логирует ошибку, возвращает `{"detail": "Internal server error"}` (без stack trace)

---

## Фаза 2: Upload Security

### 2.1 Streaming чтение файла (DoS fix)
- **Файл**: `backend/src/routers/uploads.py:50`
- Заменить `content = await file.read()` на чтение по чанкам 8KB с проверкой размера после каждого чанка

### 2.2 Валидация magic bytes (вместо расширения)
- **Файл**: `backend/src/routers/uploads.py`
- Добавить функцию `validate_image_content(content: bytes) -> str | None` — проверка JPEG (FF D8 FF), PNG (89 50 4E 47), WEBP (RIFF...WEBP) сигнатур
- Отклонять файлы с невалидным содержимым

### 2.3 Path traversal hardening
- **Файл**: `backend/src/routers/uploads.py` (delete endpoint)
- Заменить строковые проверки `"/" in filename` на `Path.resolve()` + проверку что resolved path начинается с upload_dir

### 2.4 Вынести UploadService
- **Новый файл**: `backend/src/services/upload.py`
- Методы: `get_upload_dir() -> Path`, `save_avatar(content, extension) -> str`, `delete_avatar_file(filename) -> bool`
- Упростить роутер — вызывает только сервис

---

## Фаза 3: Backend Code Quality

### 3.1 Конкретные исключения в sync_schedule
- **Файл**: `backend/src/services/schedule.py:460`
- Ловить `ParserException` отдельно от общего `Exception`

### 3.2 Атомарный set_current_semester
- **Файл**: `backend/src/services/semester.py:51-60`
- Заменить SELECT+UPDATE на один `UPDATE ... WHERE is_current=True SET is_current=False`

### 3.3 Rollback в create_work при ошибке
- **Файл**: `backend/src/services/work.py:68-108`
- Обернуть в `try/except` с `await db.rollback()` при ошибке

### 3.4 Логирование failed login
- **Файл**: `backend/src/services/auth.py`
- `logger.warning("Failed login attempt for email: %s", email)`

### 3.5 ZoneInfo вместо hardcoded timezone
- **Файл**: `backend/src/services/schedule.py:8`
- `from zoneinfo import ZoneInfo` → `OMSK_TZ = ZoneInfo("Asia/Omsk")`
- Добавить `timezone: str = "Asia/Omsk"` в `config.py`

### 3.6 Настройка structured logging
- **Файл**: `backend/src/main.py` (в lifespan)
- `setup_logging()`: `logging.basicConfig()` с форматом и уровнем в зависимости от `debug`

### 3.7 Бизнес-логика из works router в service
- **Файл**: `backend/src/services/work.py` — добавить валидацию subject в service
- **Файл**: `backend/src/routers/works.py` — упростить, убрать дублирование

### 3.8 TypedDict для SyncResult
- **Файл**: `backend/src/services/schedule.py`
- Создать `SyncResult(TypedDict)` вместо `dict[str, Any]`

---

## Фаза 4: Frontend Infrastructure

### 4.1 Error Boundary
- **Новый файл**: `frontend/src/components/ErrorBoundary.tsx`
- Class component с `getDerivedStateFromError`, fallback UI с кнопкой "Обновить страницу"
- **Файл**: `frontend/src/main.tsx` — обернуть `<App />` в `<ErrorBoundary>`

### 4.2 Fix token refresh race condition
- **Файл**: `frontend/src/lib/api.ts:37-56`
- Добавить mutex: `isRefreshing` флаг + `failedQueue` массив
- При 401 во время refresh — запросы встают в очередь, а не дублируют refresh

### 4.3 AbortController в API сервисах
- **Файлы**: все `frontend/src/services/*.ts`
- Добавить параметр `signal?: AbortSignal` в методы
- В страницах передавать signal из React Query: `queryFn: ({ signal }) => service.method(params, signal)`

### 4.4 Toast вместо alert()
- Установить `sonner` (`npm install sonner`)
- **Файл**: `frontend/src/main.tsx` — добавить `<Toaster />`
- Заменить все `alert()` на `toast.error()` / `toast.success()` в ClassmatesPage и других

### 4.5 Общий Modal компонент (+ accessibility)
- **Новый файл**: `frontend/src/components/ui/modal.tsx`
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, ESC handler, focus management
- Убрать локальные Modal из 4 страниц (SubjectsPage, WorksPage, SemestersPage, ClassmatesPage), заменить на import

### 4.6 Shared date utilities
- **Новый файл**: `frontend/src/lib/dateUtils.ts`
- `formatDeadline()`, `getDeadlineColor()`, `formatRelativeDeadline()`, `getToday()`
- Обновить DashboardPage, WorksPage, SchedulePage — использовать общие функции

### 4.7 Frontend .env.example
- **Новый файл**: `frontend/.env.example`

---

## Фаза 5: Frontend Page Fixes

### 5.1 Безопасный вывод ошибок API
- **Новый файл**: `frontend/src/lib/errorUtils.ts`
- `getErrorMessage(err, fallback)` — маппинг HTTP кодов в понятные сообщения
- Обновить LoginPage, RegisterPage

### 5.2 Спиннеры при мутациях
- **Файлы**: WorksPage, SubjectsPage, SemestersPage, ClassmatesPage
- Добавить `<Loader2 className="animate-spin" />` в кнопки при `isMutating`

### 5.3 Fix дат в календаре (timezone)
- **Файл**: `frontend/src/pages/SchedulePage.tsx:98-104`
- Заменить `date.toISOString().split('T')[0]` на явное форматирование из локальных компонентов даты

### 5.4 Санитизация Telegram ссылок
- **Файл**: `frontend/src/pages/ClassmatesPage.tsx:372`
- Фильтровать спецсимволы: `replace(/[^a-zA-Z0-9_]/g, '')`

### 5.5 Подтверждение logout
- **Файл**: `frontend/src/pages/DashboardPage.tsx:217`
- Добавить `confirm()` перед вызовом `logout()`

### 5.6 Цвета в ScheduleGrid — в constants
- **Файл**: `frontend/src/types/schedule.ts` — вынести `lessonTypeColors`

### 5.7 TIME_SLOTS — в constants
- **Новый файл**: `frontend/src/lib/constants.ts`
- Перенести из ScheduleGrid.tsx

---

## Фаза 6: Backend Minor & Nitpick

### 6.1 max_length в Pydantic-схемах
- **Файлы**: `backend/src/schemas/work.py`, `subject.py`, `classmate.py`
- Добавить `Field(max_length=...)` на description, notes и т.д.

### 6.2 Fix HttpUrl → str конвертация
- **Файл**: `backend/src/services/classmate.py`
- Вынести в хелпер `_url_to_str(url: HttpUrl | None) -> str | None`

### 6.3 Индекс на work_statuses.user_id
- **Файл**: `backend/src/models/work.py` — `index=True` на user_id FK
- **Новая миграция**: `alembic revision` → `op.create_index(...)`

### 6.4 Docstrings в exception classes
- **Файл**: `backend/src/parser/exceptions.py`
- Убрать `pass`, оставить docstrings как тело класса

### 6.5 Недостающие docstrings в сервисах
- Пройти по всем `backend/src/services/*.py`, добавить где отсутствуют

### 6.6 Type hints где отсутствуют
- **Файл**: `backend/src/routers/uploads.py` — `get_upload_dir() -> Path`

---

## Фаза 7: Frontend Minor & Nitpick

### 7.1 ESLint правила
- **Файл**: `frontend/eslint.config.js`
- Добавить: `@typescript-eslint/no-unused-vars` (с `argsIgnorePattern: '^_'`), `no-console` (warn, allow error/warn)

### 7.2 Документация DayOfWeek
- **Файл**: `frontend/src/types/schedule.ts`
- JSDoc комментарий о разнице между ISO 8601 (1-7) и JS Date (0-6)

---

## Файлы для изменения (сводка)

### Новые файлы (10):
| Файл | Фаза |
|------|------|
| `.github/workflows/ci.yml` | 0 |
| `backend/src/utils/rate_limit.py` | 1 |
| `backend/src/services/upload.py` | 2 |
| `frontend/src/components/ErrorBoundary.tsx` | 4 |
| `frontend/src/components/ui/modal.tsx` | 4 |
| `frontend/src/lib/dateUtils.ts` | 4 |
| `frontend/src/lib/errorUtils.ts` | 5 |
| `frontend/src/lib/constants.ts` | 5 |
| `frontend/.env.example` | 4 |
| Новая Alembic миграция | 6 |

### Изменяемые файлы (~20):
| Файл | Фазы |
|------|------|
| `backend/pyproject.toml` | 1 (slowapi) |
| `backend/src/config.py` | 1, 3 |
| `backend/src/main.py` | 1, 3 (CORS, security headers, exception handler, logging, limiter) |
| `backend/src/routers/auth.py` | 1 (rate limiting) |
| `backend/src/routers/uploads.py` | 2 (streaming, magic bytes, path traversal) |
| `backend/src/services/schedule.py` | 3 (exceptions, timezone, TypedDict) |
| `backend/src/services/semester.py` | 3 (atomic update) |
| `backend/src/services/work.py` | 3 (rollback, business logic) |
| `backend/src/services/auth.py` | 3 (logging) |
| `backend/src/services/classmate.py` | 6 (HttpUrl fix) |
| `backend/src/schemas/work.py`, `subject.py`, `classmate.py` | 6 (max_length) |
| `backend/src/models/work.py` | 6 (index) |
| `backend/src/parser/exceptions.py` | 6 (docstrings) |
| `frontend/src/main.tsx` | 4 (ErrorBoundary, Toaster) |
| `frontend/src/lib/api.ts` | 4 (token refresh mutex) |
| `frontend/src/pages/*.tsx` (все 6 страниц) | 4-5 (modal, toast, spinners, errors) |
| `frontend/src/services/*.ts` | 4 (AbortController) |
| `frontend/src/types/schedule.ts` | 5, 7 (colors, docs) |
| `frontend/eslint.config.js` | 7 |

---

## Отложено (отдельный PR)
- httpOnly cookies вместо localStorage (#2)
- Механизм отзыва JWT (#17)
- Docker production config (#5)

---

## Верификация

После каждой фазы:
1. **Backend**: `cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest -q`
2. **Frontend**: `cd frontend && npm run lint && npm run build`
3. **Полный тест**: push → проверить GitHub Actions зелёный
4. **Ручной тест**: login → dashboard → все страницы → upload аватара → logout
5. **Security тест**: попробовать загрузить .exe, path traversal `../../etc/passwd`, brute-force login (6+ запросов за минуту)
