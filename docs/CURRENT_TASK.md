# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит `1f2b16b` (2026-02-20): style(notes): apply ruff format to test_notes.py.

### Что сделано в этой сессии (2026-02-20):
- feat(notes): make lesson notes shared across all users
  - LessonNote переведён на shared-модель: одна заметка на предмет, видна всем
  - user_id nullable + SET NULL (last editor tracking)
  - Новое поле last_edited_by_name в API response и NoteCard UI
  - Миграция i9j0k1l2m3n4: дедупликация + пересоздание constraints
  - 5 cross-user тестов добавлено (31 backend / 15 frontend NoteCard+NotesPage)
  - CI зелёный, деплой прошёл автоматически

## Следующие шаги (по приоритету)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
