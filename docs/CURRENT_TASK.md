# Текущая задача

## Статус
**Нет активной задачи.**

## Последняя сессия: Code Review Phase 3 (Accessibility + Testing) — 2026-02-12

### Сделано
Продолжение реализации улучшений из code review плана:

**P2 — Medium (Accessibility):**
1. Frontend: `LessonCard` — добавлен `aria-label` для screen readers (2 новых теста)
2. Frontend: `LessonCard` — тесты для `hasNote` prop (2 новых теста)

**P2 — Medium (Testing):**
3. Frontend: `SchedulePage` — 12 новых интеграционных тестов:
   - Рендеринг заголовка и недели
   - Отображение записей расписания
   - Индикатор следующей пары
   - Навигация между неделями
   - Состояние ошибки с retry
   - Кнопка обновления
   - Открытие/закрытие модала деталей занятия
   - Пустое состояние
4. Frontend: MSW handlers для `/schedule/week` и `/schedule/refresh`
5. Frontend: `testWeekSchedule` тестовые данные

### Предыдущая сессия: Code Review Phase 2 — 2026-02-12
**P0 — Critical:**
1. Backend: Transaction rollback в `database.py` — автоматический откат при ошибках
2. Frontend: React.lazy() для 12 страниц (DashboardPage, SchedulePage, SubjectsPage, etc.)
3. Frontend: `PageSkeleton` компонент для Suspense fallback
4. Frontend: Global error handler (`unhandledrejection` + `error` listeners, 7 тестов)

**P1 — High:**
5. Backend: Retry модуль (`src/parser/retry.py`) с exponential backoff (19 тестов)
6. Backend: Retry интегрирован в `omsu_parser._fetch_json()` и `lk_parser.fetch_student_data()`
7. Frontend: Оптимизация DashboardPage queries (staleTime: 1-10 min, gcTime: 10-60 min)
8. Frontend: ScheduleGrid ARIA атрибуты для accessibility

### Метрики
- Backend тестов: 421 passed
- Frontend тестов: ~380 passed (добавлено 16 новых)
- Линтер: ✅ Ruff + ESLint чисто
- Build: ✅ TypeScript + Vite

### Результат
- Улучшена accessibility LessonCard (aria-label для clickable cards)
- Добавлено тестовое покрытие для SchedulePage (ключевая страница)
- Добавлены MSW handlers для week schedule endpoint

## Следующие задачи (приоритет)
1. **Бэкапы PostgreSQL** — настроить cron + pg_dump (P0)
2. **05-ics-export** — экспорт расписания в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1)

### Оставшиеся пункты Code Review (низкий приоритет):
- P1-7: Structured logging (structlog) — требует зависимость
- P1-8: Prometheus metrics — требует зависимость
- P2-11: Виртуализация в FilesPage — требует @tanstack/react-virtual
- P1-10: Переписать LK parser тесты с respx

## Блокеры / Вопросы
Нет блокеров.
