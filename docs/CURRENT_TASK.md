# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: Subgroup filter fix — 2026-02-11

### Сделано
1. Исправлен парсер: теперь извлекает подгруппу из поля `subgroupName` API
2. Добавлено поле `subgroupName` в `_extract_lessons()` (omsu_parser.py)
3. Изменён `map_api_entry()` — использует `subgroupName` вместо `group_name`
4. Обновлены тесты
5. Пересинхронизировано расписание на сервере

### Результат
- **396 записей** с подгруппой (1 или 2)
- **2692 записи** без подгруппы (общие пары)
- Фильтрация по подгруппам теперь работает

### Коммиты
- `d518fa5` — refactor(schedule): remove PE teacher select from SchedulePage
- `f926f97` — fix(parser): extract subgroup from subgroupName field
- `140e9a6` — fix(parser): pass subgroupName field to data mapper

### Деплой
✅ Задеплоено и работает: https://studyhelper1.ru

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

## Блокеры / Вопросы
Нет блокеров.
