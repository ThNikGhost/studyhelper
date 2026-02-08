# 07-progress-bars: Прогресс-бары по предметам

## Суть
Добавить визуальные прогресс-бары на SubjectsPage и Dashboard, показывающие процент выполненных работ по каждому предмету и общий прогресс семестра.

## Backend
Изменения **не требуются**. `GET /api/v1/works` возвращает все работы с `my_status` — frontend группирует по `subject_id` и считает прогресс.

---

## Шаги реализации

### 1. Утилиты расчёта прогресса `lib/progressUtils.ts` (новый)

Типы:
- `SubjectProgress` — `{ subjectId, subjectName, total, completed, inProgress, notStarted, percentage }`
- `SemesterProgress` — `{ total, completed, inProgress, notStarted, percentage, subjects: SubjectProgress[] }`

Функции:
- `calculateSemesterProgress(works, subjects)` — группировка WorkWithStatus[] по subject_id, подсчёт статусов. COMPLETED + SUBMITTED + GRADED = completed. IN_PROGRESS = inProgress. Остальное (NOT_STARTED + null) = notStarted.
- `getProgressColor(percentage)` — `text-green-600` (>=75), `text-yellow-600` (>=40), `text-red-600` (<40)
- `getProgressBarColor(percentage)` — `bg-green-500` / `bg-yellow-500` / `bg-red-500`

### 2. Компонент `ProgressBar` `components/ui/progress-bar.tsx` (новый)

Props: `{ value: number, color?: string, size?: 'sm' | 'md', showLabel?: boolean, className?: string }`
- Фон: `bg-muted rounded-full`
- Заполнение: переданный цвет или дефолтный `bg-primary`, `transition-all duration-500`
- size: sm = `h-1.5`, md = `h-2.5`
- Accessibility: `role="progressbar"`, `aria-valuenow`, `aria-valuemin=0`, `aria-valuemax=100`

### 3. Компонент `SubjectProgressCard` `components/subjects/SubjectProgressCard.tsx` (новый)

Props: `{ subject: SubjectResponse, progress: SubjectProgress | undefined, onClick?: () => void }`
- Card с названием предмета, short_name badge
- ProgressBar (md) с процентом
- Текст: "5 из 12 выполнено"
- Mini badges: кол-во по статусам (только ненулевые) — цвета из workStatusColors
- Без работ: "Нет работ" серым текстом
- onClick → навигация на WorksPage с фильтром

### 4. Виджет `SemesterProgressWidget` `components/dashboard/SemesterProgressWidget.tsx` (новый)

Props: `{ progress: SemesterProgress | undefined, isLoading, isError }`
- Card с заголовком "Прогресс семестра", иконка TrendingUp
- Общий ProgressBar + "X из Y (Z%)"
- Список: топ-3 предмета с наименьшим прогрессом (мотивация) — мини-бары
- Ссылка "Все предметы" → `/subjects`
- Loading/error states аналогично TodayScheduleWidget

### 5. Интеграция в `SubjectsPage`

- Добавить `useQuery(['works'], workService.getWorks)` для всех работ
- `useMemo` для `calculateSemesterProgress(works, subjects)`
- Заменить текущий grid карточек на `SubjectProgressCard` компоненты
- Показывать мини-summary вверху: "Общий прогресс: X%" с ProgressBar

### 6. Интеграция в `DashboardPage`

- Добавить `useQuery(['subjects'], subjectService.getSubjects)` (нужен список предметов)
- Добавить `useQuery(['works'], workService.getWorks)` для расчёта (или переиспользовать если уже есть)
- `<SemesterProgressWidget>` в grid виджетов
- Layout: grid `md:grid-cols-2`, SemesterProgressWidget под DeadlinesWidget

### 7. Сервис `subjectService` (если отсутствует) + handler

- Проверить `services/subjectService.ts` — добавить `getSubjects()` если нет
- MSW handler: `GET /api/v1/subjects`

### 8. MSW handlers обновить

- `GET /api/v1/subjects` — список предметов
- Расширить `testWorksForSubject` тестовыми данными с разными статусами

### 9. Тесты progressUtils (~10)

- calculateSemesterProgress: группировка, подсчёт, пустой список, без статуса
- getProgressColor: пороги red/yellow/green
- getProgressBarColor: аналогично

### 10. Тесты ProgressBar (~5)

- Рендеринг с value 0, 50, 100
- aria атрибуты
- Размеры sm/md
- showLabel

### 11. Тесты SubjectProgressCard (~5)

- С прогрессом, без работ
- Breakdown badges
- onClick

### 12. Тесты SemesterProgressWidget (~5)

- Рендеринг, loading, error
- Топ-3 предмета
- Ссылка

---

## Файлы (сводка)

| Файл | Действие |
|------|----------|
| `lib/progressUtils.ts` | **новый** |
| `components/ui/progress-bar.tsx` | **новый** |
| `components/subjects/SubjectProgressCard.tsx` | **новый** |
| `components/dashboard/SemesterProgressWidget.tsx` | **новый** |
| `services/subjectService.ts` | **новый** (если нет) или модифицировать |
| `pages/SubjectsPage.tsx` | модифицировать |
| `pages/DashboardPage.tsx` | модифицировать |
| `test/mocks/handlers.ts` | модифицировать |
| `lib/__tests__/progressUtils.test.ts` | **новый** (~10 тестов) |
| `components/ui/__tests__/progress-bar.test.tsx` | **новый** (~5 тестов) |
| `components/subjects/__tests__/SubjectProgressCard.test.tsx` | **новый** (~5 тестов) |
| `components/dashboard/__tests__/SemesterProgressWidget.test.tsx` | **новый** (~5 тестов) |

## Верификация
1. `cd frontend && npx tsc --noEmit` — TypeScript чисто
2. `cd frontend && npx eslint src/` — ESLint чисто
3. `cd frontend && npx vitest run` — все тесты проходят (~170+)
4. `cd frontend && npm run build` — build успешен
5. Ручная проверка: SubjectsPage показывает прогресс-бары по каждому предмету
6. Ручная проверка: Dashboard показывает виджет общего прогресса семестра
