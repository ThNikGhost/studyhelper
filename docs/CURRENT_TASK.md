# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: Subgroup filter fix & improvements — 2026-02-11

### Сделано
1. Убрана кнопка выбора преподавателя физры из SchedulePage (теперь только в Settings)
2. Исправлен парсер: извлекает подгруппу из поля `subgroupName` API (не `group_name`)
3. Добавлено поле `subgroupName` в `_extract_lessons()` (omsu_parser.py)
4. Исправлена страница настроек: всегда показывает обе подгруппы (1 и 2)
5. Добавлен индикатор "!" на пустых ячейках расписания для пар другой подгруппы

### Результат
- **396 записей** с подгруппой (1 или 2)
- **2692 записи** без подгруппы (общие пары)
- Фильтрация по подгруппам работает корректно
- Видны пары другой подгруппы (значок "!" с popover)

### Коммиты
- `d518fa5` — refactor(schedule): remove PE teacher select from SchedulePage
- `f926f97` — fix(parser): extract subgroup from subgroupName field
- `140e9a6` — fix(parser): pass subgroupName field to data mapper
- `065a4d4` — fix(settings): always show both subgroup options
- `368448a` — feat(schedule): show indicator for other subgroup's classes on empty slots

### Деплой
✅ Задеплоено и работает: https://studyhelper1.ru

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

## Блокеры / Вопросы
Нет блокеров.
