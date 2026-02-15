# Текущая задача

## Статус
**Bugfixes + Features — планирование завершено, реализация начата.**

## Последняя сессия: Documentation Cleanup — 2026-02-15

### Сделано
- Ранее: master plan (15 задач), B1-B3, B5, B6 (частично)
- project_status.md: 625 → 110 строк (-85%), убраны завершённые чеклисты
- Удалено 35 завершённых план-файлов из docs/plans/
- CLAUDE.md: обновлена ссылка на docs/plans/tasks/
- Незакоммичены: B1-B3, B5, B6 изменения в frontend (из предыдущей сессии)

## Следующие шаги (по приоритету)
1. **B6** — завершить: удалить ThemeToggle.tsx и ThemeToggle.test.tsx
2. **B7** — Remove "Notes" tab (App.tsx + QuickActions)
3. **B9** — Semester dates from LK (CRITICAL backend fix)
4. **B10** — Verification после B9
5. **B11** — File download JWT fix
6. **B4** — Schedule scroll indicator
7. **B8** — GradesPage light theme contrast
8. **B12** — Nginx healthcheck path
9. **F1** — PostgreSQL backups
10. **F2** — Sentry integration
11. **F5** — Phone widgets
12. **F3** — Telegram bot
13. **F4** — Google Calendar sync

## Блокеры / Вопросы
- B10 зависит от B9 (semester dates fix)
- F2 требует создание аккаунта Sentry
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
