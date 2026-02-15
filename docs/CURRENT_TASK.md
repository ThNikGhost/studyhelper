# Текущая задача

## Статус
**Bugfixes B1-B3, B5, B6 — завершены. Код-ревью пройдено. Готово к коммиту.**

## Последняя сессия: Code Review Fixes — 2026-02-15

### Сделано
- Код-ревью B1-B3, B5, B6 — все замечания исправлены:
  - **P0**: Удалены мёртвые файлы ThemeToggle.tsx и ThemeToggle.test.tsx
  - **P2**: Исправлена индентация в SettingsPage.tsx (строки 130-448 сдвинуты на +2 пробела)
  - **P2**: Добавлен `aria-pressed` на кнопки темы в SettingsPage.tsx
- Верификация: ESLint clean, AppLayout тесты 3/3, TypeScript clean
- Незакоммичено: B1-B3, B5, B6 изменения в frontend (7 файлов)

## Следующие шаги (по приоритету)
1. **B7** — Remove "Notes" tab (App.tsx + QuickActions)
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
