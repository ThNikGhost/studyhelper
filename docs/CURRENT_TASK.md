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
- feat(subjects): add lesson_types computed field
  - Backend: вычисляемое поле `lesson_types: list[str]` в SubjectResponse (типы занятий из всего расписания семестра)
  - Frontend: упрощён SettingsPage — кнопки типов занятий используют `subject.lesson_types` напрямую (-32 строки кода)
  - Тесты: добавлено 2 backend теста, все 644 теста проходят
  - Исправлена проблема: кнопки типов теперь отображаются для всех предметов с 2+ типами за семестр (раньше только для текущей недели)
- feat(telegram): apply hidden_subjects filter to bot commands and notifications
  - Создан модуль `telegram/schedule_utils.py` с функциями фильтрации (get_filtered_day_schedule, get_filtered_current_lesson, filter_works_by_hidden_subjects)
  - Обновлены handlers: `/today`, `/tomorrow`, `/next` — применяют пользовательский фильтр hidden_subjects
  - Обновлены notifications: `send_morning_summaries()`, `send_deadline_alerts()` — фильтруют скрытые предметы
  - Работы фильтруются только для полностью скрытых предметов (hidden_subjects[id] = null), per-type скрытие не применяется к работам
  - Тесты: 7 unit тестов (schedule_utils) + 3 integration теста, все 654 теста проходят

### Незакоммиченные изменения (10 файлов):
**PWA fix:**
- `frontend/src/components/UpdatePrompt.tsx` — periodic check + try/catch + fallback reload
- `frontend/src/components/__tests__/UpdatePrompt.test.tsx` — 8 тестов
- `frontend/src/test/pwa-mock.ts` — SW registration mock
- `frontend/src/test/setup.ts` — global test setup для PWA mocks
- `frontend/vite.config.ts` — cleanupOutdatedCaches + clientsClaim

**lesson_types feature:**
- `backend/src/schemas/subject.py` — добавлено поле lesson_types
- `backend/src/services/subject.py` — функция _get_subject_lesson_types() + вызов в get_subjects()
- `backend/tests/test_subjects.py` — 2 новых теста для lesson_types
- `frontend/src/types/subject.ts` — добавлено поле lesson_types
- `frontend/src/pages/SettingsPage.tsx` — упрощён код (-32 строки)

**Telegram hidden_subjects filter:**
- `backend/src/telegram/schedule_utils.py` — новый модуль с 3 функциями фильтрации
- `backend/src/telegram/handlers/schedule.py` — обновлены handlers для фильтрации
- `backend/src/telegram/notifications.py` — обновлены notifications для фильтрации
- `backend/tests/test_telegram_schedule_utils.py` — 7 unit тестов
- `backend/tests/test_telegram.py` — 3 integration теста

## Следующие шаги (по приоритету)
- Закоммитить и задеплоить PWA fix
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
