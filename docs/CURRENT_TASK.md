# Текущая задача

## Статус
**Нет активной задачи.** CI fix завершён.

## Последняя сессия: Fix CI

### Сделано
- [x] ESLint: `src/components/ui` добавлен в globalIgnores (shadcn/ui ошибки устранены)
- [x] CI: `uv sync --extra dev` вместо `uv sync --dev` (ruff теперь устанавливается)
- [x] Backend: кросс-платформенная path traversal защита в `delete_avatar_file` (бэкслэш + `..` отклоняются до `resolve()`)
- [x] Ruff format применён к `upload.py`

### Коммиты
1. `06c2df4` — fix(ci): fix ESLint shadcn/ui errors and backend ruff not found
2. `6478f7f` — fix(uploads): reject backslash in filename for cross-platform path traversal protection
3. `7a987d7` — style(uploads): apply ruff formatting to upload.py

### Статус CI
- Ожидает прохождения после пуша `7a987d7`

## Следующие задачи (приоритет)
1. **05-ics-export** — экспорт в .ics (P2)
2. **02-push-notifications** — push-уведомления (P1, зависит от PWA)

## Блокеры / Вопросы
Нет блокеров.
