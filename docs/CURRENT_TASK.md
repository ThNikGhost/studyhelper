# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: LK Integration — Frontend — 2026-02-12

### Сделано
1. Backend: `total_hours` поле в Subject модели + миграция `488c2925b15c`
2. Backend: `POST /api/v1/lk/import` endpoint + `import_to_app()` сервис
3. Frontend: `lkService.ts` — полный API сервис для ЛК
4. Frontend: `types/lk.ts` — типы (LkStatus, SessionGrade, LkImportResult и др.)
5. Frontend: `SettingsPage.tsx` — рабочая секция ЛК (verify/save/sync/disconnect)
6. Frontend: `SemestersPage.tsx` — кнопка "Импорт из ЛК" с confirm modal
7. Frontend: `SubjectsPage.tsx` — отображение total_hours
8. Frontend: `GradesPage.tsx` — новая страница зачётки со статистикой
9. Frontend: `QuickActions.tsx` — пункт "Зачётка"
10. Frontend: `dateUtils.ts` — `formatDistanceToNow()` utility
11. Фикс: удалён импорт LkTestPage из App.tsx (ломал build)
12. Деплой на сервер — 18 миграций, все контейнеры healthy

### Коммиты
- `a702b8f` — feat(lk): implement LK integration with grades page and import
- `1a7d6b7` — fix(frontend): remove unused LkTestPage import

### Результат
- Production задеплоен: https://studyhelper1.ru
- Новые страницы: /grades, обновлённая /settings
- 18 миграций применено
- 14 frontend страниц

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

## Блокеры / Вопросы
Нет блокеров.
