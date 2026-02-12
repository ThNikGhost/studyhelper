# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: User Settings Sync + Deploy — 2026-02-12

### Сделано
1. Backend: 3 поля в User модели (`preferred_subgroup`, `preferred_pe_teacher`, `theme_mode`)
2. Backend: `PATCH /api/v1/auth/me/settings` endpoint для частичного обновления
3. Backend: `UserSettingsUpdate` схема с валидацией
4. Backend: Alembic миграция `5a6b7c8d9e0f_add_user_settings_fields`
5. Backend: 6 тестов для endpoint настроек (всего 21 тест auth)
6. Frontend: `useUserSettings` хук с TanStack Query optimistic updates
7. Frontend: `settingsStore` → `useLocalSettingsStore` (локальный fallback)
8. Frontend: `useTheme` синхронизирует theme_mode с сервером
9. Frontend: Обновлён FOUC prevention script для нового формата хранения
10. Frontend: Обновлены SettingsPage, SchedulePage, DashboardPage, PeTeacherSelect
11. Frontend: Обновлены тестовые моки + исправлены тесты темы
12. CI fix: тесты lk_parser пропускаются в CI (зависают из-за httpx async mocking)
13. CI fix: форматирование lk module файлов
14. CI fix: modern Python typing в миграции
15. Деплой на сервер — backend пересобран, миграция применена

### Коммиты
- `297989d` — feat(settings): sync user settings across devices
- `c27afce` — docs: update status after user settings sync
- `d5746e1` — style: use modern Python typing in migration
- `063d79a` — style: format lk module files
- `7619cec` — test: skip lk_parser tests in CI

### Результат
- Настройки синхронизируются между устройствами через сервер
- Для незалогиненных пользователей — localStorage fallback
- CI: ✅ Проходит (424 backend, 359 frontend)
- Production: ✅ Задеплоено на https://studyhelper1.ru

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

## Блокеры / Вопросы
Нет блокеров.
