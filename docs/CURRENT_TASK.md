# Текущая задача

## Статус
**B9 завершена. Следующая: B10 (verification после B9).**

## Последняя сессия: B9 Semester dates from LK — 2026-02-15

### Сделано
- **B9**: Исправлен `import_to_app()` — текущий семестр определяется по session grades, а не max(disciplines)
- Новая функция `_determine_current_semester()`: парсит session_number, current = max+1, capped by study plan
- Авто-заполнение `start_date`/`end_date` (осень: Sep1-Dec30, весна: Feb9-Jul7)
- Ручные даты не перезаписываются при re-import
- `is_current` обновляется при каждом import (не только при create)
- 5 новых тестов в `TestLkImport`, все 471 тест зелёные

## Следующие шаги (по приоритету)
1. **B10** — Verification после B9 (re-import на проде)
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
