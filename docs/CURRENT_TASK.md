# Текущая задача

## Статус
**06-clickable-schedule завершена** — реализована на ветке `main`, ожидает коммит.

## Выполнено: 06-clickable-schedule (кликабельные элементы расписания)
- [x] `ScheduleEntryUpdate` тип в `types/schedule.ts`
- [x] `updateEntry()` метод в `scheduleService.ts`
- [x] `LessonDetailModal` — новый компонент с полной информацией, работами по предмету, редактируемыми заметками
- [x] `LessonCard` — onClick prop, cursor-pointer hover, keyboard a11y (Enter/Space), role="button"
- [x] `ScheduleGrid` — onEntryClick prop, hover:opacity-80, keyboard a11y
- [x] `DayScheduleCard` — onEntryClick проброс в LessonCard
- [x] `TodayScheduleWidget` — onEntryClick prop, LessonRow кликабельный с hover:bg-accent/50
- [x] `SchedulePage` — selectedEntry state + LessonDetailModal
- [x] `DashboardPage` — selectedEntry state + LessonDetailModal
- [x] MSW handlers: PUT schedule entry, GET works с фильтром subject_id
- [x] `tsconfig.app.json` — exclude тестовых файлов из build (fix pre-existing issue)
- [x] 19 тестов LessonDetailModal (рендеринг, работы, заметки, toast, a11y)
- [x] 12 тестов LessonCard (рендеринг, onClick, keyboard, notes, subgroup)
- [x] TypeScript, ESLint, build — всё чисто
- [x] 145 frontend тестов проходят (было 114, +31 новых)

## Следующие задачи (приоритет)
1. **09-dark-theme** — тёмная тема (P2)
2. **07-progress-bars** — прогресс-бары по предметам (P2)
3. **03-file-upload-ui** — UI загрузки файлов (P1)
4. **05-ics-export** — экспорт в .ics (P2)
5. **02-push-notifications** — push-уведомления (P1, зависит от PWA ✅)
6. **08-attendance** — посещаемость (P2)
7. **10-lesson-notes** — заметки к парам (P2)
8. **11-semester-timeline** — timeline семестра (P3)

## Заметки
- Backend: 264 теста проходят
- Frontend: 145 тестов проходят
- Все линтеры чисты
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
