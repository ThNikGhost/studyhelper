# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит (2026-02-23): feat(files): add category editing and open-in-browser support (aaa4d8e).

### Что сделано в этой сессии (2026-02-23):
- Backend: `PATCH /files/{id}` endpoint — изменение категории файла (owner-only, 403 для чужих)
- Backend: схема `FileUpdateRequest`, сервис `update_file_category()`
- Frontend: `fileService.updateFileCategory()` + `openFile()` (открытие blob в новой вкладке)
- Frontend: `canOpenInBrowser()` utility в fileUtils (PDF + image/*)
- Frontend: inline-редактирование категории в FileList — карандаш при hover, select dropdown
- Frontend: кнопка ExternalLink для PDF/изображений в FileList
- Тесты: 3 новых теста для PATCH endpoint, итого 668 backend тестов
- Все проверки прошли: ruff clean, ESLint clean, Vite build OK

## Следующие шаги (по приоритету)
- Задеплоить новые фичи на прод (`git pull` + `docker compose restart backend`)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
