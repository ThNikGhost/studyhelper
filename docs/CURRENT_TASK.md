# Текущая задача

## Статус
**B7 завершена и закоммичена. Следующая: B9 (semester dates from LK).**

## Последняя сессия: B7 Remove Notes Tab — 2026-02-15

### Сделано
- **B7**: Удалён route `/notes` из App.tsx и карточка "Заметки" из QuickActions
- Code review пройден — Approved
- Коммит: `65aae8c fix(frontend): remove Notes tab from navigation (B7)`
- Заметки по-прежнему доступны через LessonDetailModal в расписании

## Следующие шаги (по приоритету)
1. **B9** — Semester dates from LK (CRITICAL backend fix)
2. **B10** — Verification после B9
3. **B11** — File download JWT fix
4. **B4** — Schedule scroll indicator
5. **B8** — GradesPage light theme contrast
6. **B12** — Nginx healthcheck path
7. **F1** — PostgreSQL backups
8. **F2** — Sentry integration
9. **F5** — Phone widgets
10. **F3** — Telegram bot
11. **F4** — Google Calendar sync

## Блокеры / Вопросы
- B10 зависит от B9 (semester dates fix)
- F2 требует создание аккаунта Sentry
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
