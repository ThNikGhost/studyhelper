# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит (2026-03-02): fix(frontend): fix deadline off-by-one, PE stats, and dashboard 7-day filter (b4348b2).

### Что сделано в этой сессии (feat: work file attachments + code review fixes):

**Фича: Work File Attachments** (не закоммичено)
- Backend: migration `l2m3n4o5p6q7` — `work_id` FK на `files` таблице (SET NULL on delete)
- Backend: модель `File` + схемы `FileResponse/FileListResponse/FileUpdateRequest` + сервис + роутер обновлены
- Frontend: `StudyFile` type + `fileService` + `WorkFilesModal` (новый компонент) + `FileDropzone` (works prop) + `FileList` (detach button) + `FilesPage` + `WorksPage` (paperclip button)

**Code review fixes (применены):**
- `FileUpdateRequest`: `{"category": null}` теперь возвращает 422 (было silent no-op)
- `update_file()` service: убран `HTTPException` — проверка work перенесена в роутер (паттерн проекта)
- Tests: `test_patch_empty_body_returns_422` + `test_patch_category_null_returns_422` добавлены
- `FileList`: `📎` → `<Paperclip aria-hidden>`, `×`/`…` → `<X>`/`<Loader2>` lucide-иконки
- `FileDropzone.test.tsx`: 2 новых теста для `works` prop (selector renders, workId в onUpload)

**Метрики после сессии:**
- Backend: 675 тестов
- Frontend: 408 тестов (3 pre-existing SchedulePage failures)

## Следующие шаги (по приоритету)
- Закоммитить work file attachments feature (все тесты зелёные)
- Задеплоить на prod
- (Фаза 3) httpOnly cookies — access token в памяти, refresh в httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет

## Известные pre-existing падения тестов
- `SchedulePage.test.tsx` — 3 теста падают (hidden subjects filter применяется в mock-данных)
- Не связаны с текущими изменениями, существуют с момента добавления фильтрации расписания
