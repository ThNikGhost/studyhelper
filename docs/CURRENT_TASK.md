# Текущая задача

## Статус
**03-file-upload-ui завершена** — реализована на ветке `main`, ожидает коммит.

## Выполнено: 03-file-upload-ui (файловое хранилище)

### Backend
- [x] `models/file.py` — модель File (id, filename, stored_filename, mime_type, size, category, subject_id FK, uploaded_by FK, created_at)
- [x] `schemas/file.py` — FileCategory StrEnum, FileResponse, FileListResponse
- [x] `services/file.py` — upload_file, get_files, get_file_by_id, delete_file, path traversal protection
- [x] `services/upload.py` — _FILE_SIGNATURES, validate_file_content(), параметризованный read_upload_streaming(max_size_mb)
- [x] `routers/files.py` — POST /upload, GET /, GET /{id}/download, DELETE /{id}
- [x] `config.py` — max_file_size_mb=50, allowed_file_extensions, allowed_file_mime_types
- [x] `models/__init__.py` — File в импорты
- [x] `main.py` — files router
- [x] Alembic миграция add_files_table
- [x] 21 backend тестов (upload: 10, list: 5, download: 3, delete: 3)

### Frontend
- [x] `types/file.ts` — FileCategory, fileCategoryLabels, StudyFile interface
- [x] `services/fileService.ts` — uploadFile (onProgress), getFiles, deleteFile, getDownloadUrl
- [x] `lib/fileUtils.ts` — formatFileSize, getFileIcon, isAllowedFileType, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS
- [x] `components/files/FileDropzone.tsx` — HTML5 drag & drop, file preview, category/subject selects, progress bar, disabled state
- [x] `components/files/FileList.tsx` — список файлов с иконками, metadata, download/delete
- [x] `pages/FilesPage.tsx` — dropzone, фильтры, список, модал удаления, TanStack Query
- [x] `App.tsx` — маршрут /files (ProtectedRoute + AppLayout)
- [x] `QuickActions.tsx` — пункт "Файлы" (FolderOpen, text-amber-500)
- [x] MSW handlers: GET /files/, POST /files/upload, DELETE /files/:id, testFiles data
- [x] 43 frontend тестов (fileUtils: 20, FileDropzone: 8, FileList: 7, FilesPage: 8)
- [x] TypeScript, ESLint, build — всё чисто

## Следующие задачи (приоритет)
1. **09-dark-theme** — тёмная тема (P2)
2. **05-ics-export** — экспорт в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1, зависит от PWA)
4. **08-attendance** — посещаемость (P2)
5. **10-lesson-notes** — заметки к парам (P2)
6. **11-semester-timeline** — timeline семестра (P3)

## Заметки
- Backend: 285 тестов проходят (264 + 21 новых)
- Frontend: 226 тестов проходят (183 + 43 новых)
- Все линтеры чисты
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
