# Текущая задача

## Статус
**B8 завершена. Следующая: B12 (Nginx healthcheck path).**

## Последняя сессия: B8 GradesPage light theme contrast — 2026-02-15

### Сделано
- **B8**: Добавлены `border border-*-200 dark:border-*-800` ко всем вариантам в `getGradeColor()`
- 6 вариантов оценок: отлично, хорошо, удовл., зачтено, неудовл., прочее
- Fallback (gray) использует `dark:border-gray-700` (не 800) — чтобы border не сливался с `dark:bg-gray-800`
- Lint + build чистые, code review пройден

## Следующие шаги (по приоритету)
1. **B12** — Nginx healthcheck path
2. **F1** — PostgreSQL backups
3. **F2** — Sentry integration
4. **F5** — Phone widgets
5. **F3** — Telegram bot
6. **F4** — Google Calendar sync

## Блокеры / Вопросы
- F2 требует создание аккаунта Sentry
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
- 8 локальных коммитов не запушены на origin
