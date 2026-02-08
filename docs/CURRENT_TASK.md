# Текущая задача

## Статус
**11-semester-timeline завершена** — реализована, ожидает коммит.

## Выполнено: 11-semester-timeline (timeline семестра)

### Backend
- [x] `models/semester.py` — добавлены start_date/end_date (Date, nullable)
- [x] `schemas/semester.py` — start_date/end_date в SemesterBase/SemesterUpdate, model_validator, TimelineDeadline/TimelineExam/TimelineResponse
- [x] `services/semester.py` — start_date/end_date в create_semester, get_semester_timeline()
- [x] `routers/semesters.py` — GET /{semester_id}/timeline (400 no dates, 404 not found)
- [x] Alembic миграция add_semester_dates (a3b4c5d6e7f8, down_revision: d62cab669757)
- [x] 9 новых backend тестов (create/update with dates, invalid dates, timeline: success/deadlines/no_dates/not_found/unauthorized/empty)

### Frontend
- [x] `types/subject.ts` — start_date/end_date в Semester, SemesterCreate, SemesterUpdate
- [x] `types/timeline.ts` — TimelineDeadline, TimelineExam, TimelineData
- [x] `services/subjectService.ts` — getSemesterTimeline()
- [x] `lib/timelineUtils.ts` — getPositionPercent, getMonthLabels, getSemesterProgress, getMarkerColor, getExamMarkerColor
- [x] `components/timeline/TimelineBar.tsx` — горизонтальная полоса с маркерами, "Сегодня", ось месяцев
- [x] `components/timeline/TimelineMarker.tsx` — маркер с Popover tooltip (circle/diamond)
- [x] `components/timeline/TimelineLegend.tsx` — легенда цветов
- [x] `components/timeline/TimelineEventList.tsx` — хронологический список событий
- [x] `pages/TimelinePage.tsx` — фильтры (showDeadlines, showExams, subject), loading/error/empty states
- [x] `components/dashboard/SemesterTimelineWidget.tsx` — упрощённый виджет для Dashboard
- [x] `pages/SemestersPage.tsx` — date pickers в форме создания/редактирования, отображение дат
- [x] `pages/DashboardPage.tsx` — SemesterTimelineWidget + queries
- [x] `App.tsx` — маршрут /timeline (ProtectedRoute + AppLayout)
- [x] `QuickActions.tsx` — пункт "Timeline" (BarChart3, text-indigo-500)
- [x] MSW handlers + testSemester/testTimelineDeadlines/testTimelineExams/testTimelineData
- [x] 42 новых frontend теста (timelineUtils: 21, TimelineBar: 8, SemesterTimelineWidget: 5, TimelinePage: 8)
- [x] TypeScript, ESLint, build — всё чисто

## Следующие задачи (приоритет)
1. **09-dark-theme** — тёмная тема (P2)
2. **05-ics-export** — экспорт в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1, зависит от PWA)

## Заметки
- Backend: 337 тестов проходят (328 + 9 новых)
- Frontend: 321 тестов проходят (279 + 42 новых)
- Все линтеры чисты
- Timeline: чистый CSS/Tailwind позиционирование (left: X%), без chart libraries
- Маркеры дедлайнов цветокодированы: green (completed), yellow (in_progress), red (overdue), gray (future)
- Экзамены: diamond shape, purple
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
