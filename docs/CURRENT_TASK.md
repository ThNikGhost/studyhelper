# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит `d1702ad` (2026-02-21): feat(files): support multiple file upload.

### Что сделано в этой сессии (2026-02-21):
- feat(files): multiple file upload support
  - FileDropzone: multiple input, список файлов в очереди, удаление отдельного файла
  - Кнопка "Загрузить (N)" при нескольких файлах
  - FilesPage: последовательная загрузка, суммарный прогресс 0–100%, один toast в конце
  - 3 новых теста (multiple files, remove from queue, onUpload with array), 11/11 ✅

## Следующие шаги (по приоритету)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
