# Текущая задача

## Статус
**04-dashboard-widget завершена** — реализована на ветке `main`, ожидает коммит.

## Выполнено: 04-dashboard-widget (улучшение виджетов Dashboard)
- [x] `formatTime()`, `formatTimeUntil()` добавлены в dateUtils + 7 тестов
- [x] `TodayScheduleWidget` — все пары на сегодня, текущая подсвечена, прошедшие приглушены + 10 тестов
- [x] `DeadlinesWidget` — группировка по срочности, badge просроченных, до 8 элементов + 10 тестов
- [x] `QuickActions` — вынесен в отдельный компонент, адаптивная сетка
- [x] Рефакторинг DashboardPage — import новых компонентов, query `/schedule/today`
- [x] MSW handlers + DashboardPage тесты обновлены
- [x] TypeScript, ESLint, build — всё чисто
- [x] 114 frontend тестов проходят (было 87, +27 новых)

## Следующие задачи (приоритет)
1. **06-clickable-schedule** — кликабельные элементы расписания (P1)
2. **09-dark-theme** — тёмная тема (P2)
3. **07-progress-bars** — прогресс-бары по предметам (P2)
4. **03-file-upload-ui** — UI загрузки файлов (P1)
5. **05-ics-export** — экспорт в .ics (P2)
6. **02-push-notifications** — push-уведомления (P1, зависит от PWA ✅)
7. **08-attendance** — посещаемость (P2)
8. **10-lesson-notes** — заметки к парам (P2)
9. **11-semester-timeline** — timeline семестра (P3)

## Заметки
- Backend: 264 теста проходят
- Frontend: 114 тестов проходят
- Все линтеры чисты
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
