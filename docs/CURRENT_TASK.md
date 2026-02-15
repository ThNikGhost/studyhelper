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
1. **B10** — Verification после B9 (re-import на проде: `POST /api/v1/lk/import`)
2. **B11** — File download JWT fix
3. **B4** — Schedule scroll indicator
4. **B8** — GradesPage light theme contrast
5. **B12** — Nginx healthcheck path
6. **F1** — PostgreSQL backups
7. **F2** — Sentry integration
8. **F5** — Phone widgets
9. **F3** — Telegram bot
10. **F4** — Google Calendar sync

## Блокеры / Вопросы
- B10 разблокирована (B9 завершена), требует деплой на прод
- F2 требует создание аккаунта Sentry
- F3 требует Telegram Bot Token
- F4 требует Google Cloud Console проект
