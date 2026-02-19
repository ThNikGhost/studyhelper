# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит `c8d6f70` (2026-02-19): docs: update status after per-lesson-type subject hiding.

### Что сделано в этой сессии (2026-02-20):
- fix(pwa): code review + fix UpdatePrompt.tsx
  - Добавлен try/catch вокруг fetch в periodic SW update check (предотвращает unhandled promise rejection при сетевых ошибках)
  - PWA update prompt: hourly SW checks, fallback reload через 2с, workbox cleanupOutdatedCaches + clientsClaim
  - Тесты UpdatePrompt: 8 тестов (render/no-render, offline banner, update banner, click handlers, dismiss, fallback reload)
  - vite.config.ts: cleanupOutdatedCaches + clientsClaim в SW config
  - test/setup.ts + pwa-mock.ts: корректные моки для virtual:pwa-register/react
- Code review: выявлены и задокументированы 5 notes (setInterval cleanup, setTimeout cleanup, clientsClaim safety, test mock restore, dead branch) — все осознанно оставлены без исправления

### Незакоммиченные изменения (5 файлов, +112/-9):
- `frontend/src/components/UpdatePrompt.tsx` — periodic check + try/catch + fallback reload
- `frontend/src/components/__tests__/UpdatePrompt.test.tsx` — 8 тестов
- `frontend/src/test/pwa-mock.ts` — SW registration mock
- `frontend/src/test/setup.ts` — global test setup для PWA mocks
- `frontend/vite.config.ts` — cleanupOutdatedCaches + clientsClaim

## Следующие шаги (по приоритету)
- Закоммитить и задеплоить PWA fix
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
