# Текущая задача

## Статус
**07-progress-bars завершена** — реализована на ветке `main`, ожидает коммит.

## Выполнено: 07-progress-bars (прогресс-бары по предметам)
- [x] `lib/progressUtils.ts` — типы SubjectProgress/SemesterProgress, функции calculateSemesterProgress, getProgressColor, getProgressBarColor
- [x] `components/ui/progress-bar.tsx` — ProgressBar компонент (value, color, size, showLabel, a11y)
- [x] `components/subjects/SubjectProgressCard.tsx` — карточка предмета с прогресс-баром, статистикой, status badges
- [x] `components/dashboard/SemesterProgressWidget.tsx` — виджет общего прогресса семестра, топ-3 предмета с наименьшим прогрессом
- [x] `pages/SubjectsPage.tsx` — интеграция: общий прогресс вверху, SubjectProgressCard вместо простых карточек, навигация на WorksPage
- [x] `pages/DashboardPage.tsx` — интеграция: SemesterProgressWidget в grid виджетов
- [x] MSW handlers: GET /api/v1/subjects, расширенные тестовые данные работ (3 предмета, разные статусы)
- [x] 15 тестов progressUtils (группировка, подсчёт, пустые данные, цвета)
- [x] 8 тестов ProgressBar (aria, value 0/50/100, clamp, label, color)
- [x] 7 тестов SubjectProgressCard (рендеринг, badges, onClick, keyboard)
- [x] 8 тестов SemesterProgressWidget (рендеринг, loading, error, top-3, ссылка)
- [x] Обновлён DashboardPage.test.tsx (getAllByText для дублирующихся названий предметов)
- [x] TypeScript, ESLint, build — всё чисто
- [x] 183 frontend тестов проходят (было 145, +38 новых)

## Следующие задачи (приоритет)
1. **09-dark-theme** — тёмная тема (P2)
2. **03-file-upload-ui** — UI загрузки файлов (P1)
3. **05-ics-export** — экспорт в .ics (P2)
4. **02-push-notifications** — push-уведомления (P1, зависит от PWA)
5. **08-attendance** — посещаемость (P2)
6. **10-lesson-notes** — заметки к парам (P2)
7. **11-semester-timeline** — timeline семестра (P3)

## Заметки
- Backend: 264 теста проходят
- Frontend: 183 тестов проходят
- Все линтеры чисты
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
