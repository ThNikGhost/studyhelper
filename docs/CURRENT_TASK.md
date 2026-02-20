# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит `f3d28a6` (2026-02-20): feat(notes): make lesson notes shared across all users.

### Что сделано в этой сессии (2026-02-20):
- feat(notes): make lesson notes shared across all users
  - LessonNote переведён на shared-модель: одна заметка на предмет, видна всем
  - user_id nullable + SET NULL (last editor tracking)
  - Новое поле last_edited_by_name в API response и NoteCard UI
  - Миграция i9j0k1l2m3n4: дедупликация + пересоздание constraints
  - Добавлены 5 cross-user тестов (31 backend / 15 frontend, все зелёные)

### Ранее (2026-02-20, предыдущие коммиты):
- fix(pwa): code review + fix UpdatePrompt.tsx (try/catch, cleanupOutdatedCaches, clientsClaim)
- feat(subjects): add lesson_types computed field (backend + frontend SettingsPage)
- feat(telegram): apply hidden_subjects filter to bot commands and notifications

## Следующие шаги (по приоритету)
- Задеплоить на прод (git pull + docker compose build + up)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
