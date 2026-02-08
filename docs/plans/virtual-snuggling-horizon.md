# План: 03-file-upload-ui — Файловое хранилище

## Обзор

Реализация полноценного модуля файлового хранилища: backend (модель, API) + frontend (drag & drop, страница файлов). Файлы привязываются к предметам (Subject), категоризируются. Лимит 50 MB.

**Текущее состояние:** Backend имеет только upload аватаров (`POST/DELETE /api/v1/uploads/avatar`). Нет модели File в БД, нет frontend UI для файлов.

---

## Фаза 1: Backend — модель + миграция + конфигурация

### 1.1. Создать `backend/src/models/file.py`
- Модель `File(Base)` с `created_at` (без `updated_at` — файлы immutable)
- Поля: `id`, `filename` (оригинальное), `stored_filename` (UUID на диске), `mime_type`, `size`, `category`, `subject_id` (FK nullable), `uploaded_by` (FK)
- Indexes: `subject_id`, `category`, `uploaded_by`
- Relationships: `subject` → Subject, `uploader` → User

### 1.2. Обновить `backend/src/models/__init__.py`
- Добавить `from src.models.file import File` и в `__all__`

### 1.3. Обновить `backend/src/config.py`
- `max_file_size_mb: int = 50`
- `allowed_file_extensions: list[str]` — pdf, doc, docx, xls, xlsx, ppt, pptx, jpg, jpeg, png, gif, webp
- `allowed_file_mime_types: list[str]` — соответствующие MIME типы

### 1.4. Alembic миграция
- `uv run alembic revision --autogenerate -m "add_files_table"`
- `uv run alembic upgrade head`

---

## Фаза 2: Backend — сервис + роутер

### 2.1. Расширить `backend/src/services/upload.py`
- Добавить `_FILE_SIGNATURES` (PDF: `%PDF`, ZIP-based docx/xlsx/pptx: `PK\x03\x04`, OLE2 doc/xls/ppt: `\xd0\xcf\x11\xe0`, GIF: `GIF8`)
- Добавить `validate_file_content(content: bytes, extension: str) -> bool`
- Параметризовать `read_upload_streaming(file, max_size_mb=None)` для переиспользования

### 2.2. Создать `backend/src/schemas/file.py`
- `FileCategory` — константы (textbook, problem_set, lecture, lab, cheatsheet, other)
- `FileResponse(BaseModel)` — id, filename, stored_filename, mime_type, size, category, subject_id, subject_name, uploaded_by, created_at
- `FileListResponse` — то же, для списка

### 2.3. Создать `backend/src/services/file.py`
- `upload_file(db, file, category, subject_id, user_id)` → File
- `get_files(db, subject_id?, category?)` → list[File] (с join на Subject для subject_name)
- `get_file_by_id(db, file_id)` → File | None
- `delete_file(db, file)` → None (удаляет из БД + с диска)
- `get_file_storage_dir()` → Path (`uploads/files/`)
- `get_file_path(stored_filename)` → Path (с path traversal protection)

### 2.4. Создать `backend/src/routers/files.py`
- `POST /upload` — multipart/form-data (file + category Form + subject_id Form), → 201 + FileResponse
- `GET /` — список файлов, Query params: subject_id?, category?, → list[FileListResponse]
- `GET /{file_id}/download` — StreamingResponse + Content-Disposition с оригинальным именем
- `DELETE /{file_id}` — удаление, → 204

### 2.5. Обновить `backend/src/main.py`
- `from src.routers import files`
- `api_v1.include_router(files.router, prefix="/files", tags=["Files"])`

---

## Фаза 3: Backend — тесты

### 3.1. Создать `backend/tests/test_files.py`
~18 тестов:
- **Upload:** success (PDF), with subject_id, DOCX format, image, invalid type (exe), too large (>50MB), invalid category, invalid magic bytes, unauthorized, nonexistent subject
- **List:** empty, all, filter by subject, filter by category, unauthorized
- **Download:** success + Content-Disposition, not found, unauthorized
- **Delete:** success + file removed from disk, not found, unauthorized

---

## Фаза 4: Frontend — типы + сервис + утилиты

### 4.1. Создать `frontend/src/types/file.ts`
- `FileCategory` as const object + type
- `fileCategoryLabels` — русские названия
- `StudyFile` interface (название `StudyFile`, не `File`, чтобы не конфликтовать с Web API `File`)
- `fileCategoryIcons` — иконки lucide-react по категории

### 4.2. Создать `frontend/src/services/fileService.ts`
- `uploadFile({ file, category, subject_id, onProgress })` — multipart/form-data + `onUploadProgress`
- `getFiles(subjectId?, category?, signal?)` → StudyFile[]
- `deleteFile(id)` → void
- `getDownloadUrl(id)` → string URL

### 4.3. Создать `frontend/src/lib/fileUtils.ts`
- `formatFileSize(bytes)` → "1.5 MB"
- `getFileIcon(mimeType)` → LucideIcon
- `isAllowedFileType(file)` → boolean
- `MAX_FILE_SIZE_MB`, `ALLOWED_EXTENSIONS` — константы

---

## Фаза 5: Frontend — компоненты

### 5.1. Создать `frontend/src/components/files/FileDropzone.tsx`
- Нативный HTML5 Drag & Drop (без библиотек)
- Визуальное состояние при перетаскивании (border highlight)
- Кнопка "Выбрать файл" как fallback
- Select для категории (обязательное)
- Select для предмета (опциональное)
- Превью выбранного файла (имя, размер)
- Прогресс-бар загрузки (переиспользуем `ProgressBar`)
- Клиентская валидация (тип, размер) до отправки
- disabled при офлайне

### 5.2. Создать `frontend/src/components/files/FileList.tsx`
- Список/карточки файлов с иконками по типу (lucide-react: FileText, FileSpreadsheet, Presentation, Image)
- Метаданные: имя, категория badge, размер, дата, предмет
- Кнопки: скачать (ссылка), удалить (с подтверждением через Modal)
- Empty state
- Loading state

---

## Фаза 6: Frontend — страница + интеграция

### 6.1. Создать `frontend/src/pages/FilesPage.tsx`
- Header с кнопкой "назад" и "обновить"
- `FileDropzone` вверху страницы
- Фильтры: предмет (select) + категория (select)
- `FileList` с результатами
- TanStack Query: `useQuery(['files', filters])`, `useMutation` для upload/delete
- `useNetworkStatus()` — disable upload/delete в офлайне
- Модал подтверждения удаления

### 6.2. Обновить `frontend/src/App.tsx`
- Импорт `FilesPage`, маршрут `/files` (ProtectedRoute + AppLayout)

### 6.3. Обновить `frontend/src/components/dashboard/QuickActions.tsx`
- Добавить пункт "Файлы" (icon: `FolderOpen`, href: `/files`, color: `text-amber-500`)

---

## Фаза 7: Frontend — тесты

### 7.1. Создать `frontend/src/lib/__tests__/fileUtils.test.ts` (~12 тестов)
- formatFileSize: bytes, KB, MB, GB, 0, edge cases
- isAllowedFileType: allowed vs disallowed
- getFileIcon: mapping по MIME types

### 7.2. Создать `frontend/src/components/files/__tests__/FileDropzone.test.tsx` (~8 тестов)
- Default render
- File selection via input
- Drag & drop visual feedback
- Upload progress
- Reject invalid file type
- Reject oversized file
- Disabled state

### 7.3. Создать `frontend/src/components/files/__tests__/FileList.test.tsx` (~7 тестов)
- Render file list
- Empty state
- Delete button interaction
- Download link
- File size display

### 7.4. Создать `frontend/src/pages/__tests__/FilesPage.test.tsx` (~8 тестов)
- Full page render
- Upload flow
- Delete flow
- Filter interaction
- Error/loading states

### 7.5. Обновить `frontend/src/test/mocks/handlers.ts`
- MSW handlers для `GET /api/v1/files`, `POST /api/v1/files/upload`, `DELETE /api/v1/files/:id`
- Test data factory: `testFiles: StudyFile[]`

---

## Сводка файлов

### Новые (14 файлов):
| Файл | Описание |
|------|----------|
| `backend/src/models/file.py` | Модель File |
| `backend/src/schemas/file.py` | Pydantic схемы |
| `backend/src/services/file.py` | Бизнес-логика |
| `backend/src/routers/files.py` | API endpoints |
| `backend/alembic/versions/xxxx_add_files_table.py` | Миграция |
| `backend/tests/test_files.py` | Backend тесты (~18) |
| `frontend/src/types/file.ts` | TypeScript типы |
| `frontend/src/services/fileService.ts` | API сервис |
| `frontend/src/lib/fileUtils.ts` | Утилиты |
| `frontend/src/components/files/FileDropzone.tsx` | Drag & Drop |
| `frontend/src/components/files/FileList.tsx` | Список файлов |
| `frontend/src/pages/FilesPage.tsx` | Страница /files |
| `frontend/src/lib/__tests__/fileUtils.test.ts` | Тесты утилит |
| `frontend/src/components/files/__tests__/FileDropzone.test.tsx` | Тесты dropzone |

### Модифицируемые (6 файлов):
| Файл | Изменение |
|------|-----------|
| `backend/src/config.py` | +3 настройки файлов |
| `backend/src/models/__init__.py` | +File в импорты |
| `backend/src/services/upload.py` | +_FILE_SIGNATURES, +validate_file_content, параметризация read_upload_streaming |
| `backend/src/main.py` | +files router |
| `frontend/src/App.tsx` | +маршрут /files |
| `frontend/src/components/dashboard/QuickActions.tsx` | +пункт "Файлы" |
| `frontend/src/test/mocks/handlers.ts` | +MSW handlers для files |

---

## Верификация

1. **Backend тесты:** `cd backend && uv run pytest tests/test_files.py -v`
2. **Backend все тесты:** `cd backend && uv run pytest`
3. **Backend линтер:** `cd backend && uv run ruff check . && uv run ruff format --check .`
4. **Frontend тесты:** `cd frontend && npx vitest run`
5. **Frontend линтер:** `cd frontend && npm run lint`
6. **Frontend build:** `cd frontend && npm run build`
7. **Ручная проверка:** запустить backend + frontend, загрузить PDF, скачать, удалить, проверить фильтрацию
