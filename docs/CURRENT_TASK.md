# Текущая задача

## Статус
**F3 Telegram bot задеплоен на прод. F3.1 (simplify bot) завершена. Следующая: F5 (Phone widgets).**

## Последняя сессия: F3.1 Telegram Bot Simplification — 2026-02-15

### Сделано
- **Удалены команды**: `/week`, `/grades`, `/attendance` — редко используемые, дублируют web UI
- **Reply keyboard**: Добавлена `ReplyKeyboardMarkup` с двумя кнопками: «📚 Расписание на сегодня» и «⏭ Следующее занятие»
- **Обработчики кнопок**: `F.text` handlers делегируют в `cmd_today` / `cmd_next`
- **Справка обновлена**: `/start` показывает только актуальные команды
- **reply_markup**: `/start`, `/link` (после привязки), `/today`, `/tomorrow`, `/next` отправляют с `main_keyboard()`
- **ruff format**: Отформатировано 10 файлов telegram-модуля (CI format check фиксил)
- **Telegram menu**: `setMyCommands` обновлён — 9 команд вместо 12
- **Deploy**: Backend пересобран и задеплоен, webhook работает, бот `@studyhelpernik_bot` онлайн
- **CI**: GitHub Actions — success

### Файлы изменены
- `backend/src/telegram/keyboards.py` — добавлена `main_keyboard()`
- `backend/src/telegram/handlers/schedule.py` — удалён `/week`, добавлены btn_today/btn_next
- `backend/src/telegram/handlers/academics.py` — удалены `/grades`, `/attendance`
- `backend/src/telegram/handlers/start.py` — обновлена справка, добавлен reply_markup
- 6 файлов telegram-модуля — ruff format

## Следующие шаги (по приоритету)
1. **F5** — Phone widgets
2. **F4** — Google Calendar sync

## Блокеры / Вопросы
- F4 требует Google Cloud Console проект
