# Текущая задача

## Статус
**B4 завершена. Следующая: B8 (GradesPage light theme contrast).**

## Последняя сессия: B4 Schedule scroll indicator — 2026-02-15

### Сделано
- **B4**: Добавлен fade-градиент справа в ScheduleGrid на мобильных (`sm:hidden`)
- `useState` + `onScroll` handler для отслеживания позиции горизонтального скролла
- Градиент исчезает при достижении конца скролла (порог 10px)
- `pointer-events-none` — градиент не блокирует клики
- Lint + build чистые, code review пройден

## Следующие шаги (по приоритету)
1. **B8** — GradesPage light theme contrast
2. **B12** — Nginx healthcheck path
3. **F1** — PostgreSQL backups
4. **F2** — Sentry integration
5. **F5** — Phone widgets
6. **F3** — Telegram bot
7. **F4** — Google Calendar sync

## Блокеры / Вопросы
- F2 требует создание аккаунта Sentry
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
- 6 локальных коммитов не запушены на origin
