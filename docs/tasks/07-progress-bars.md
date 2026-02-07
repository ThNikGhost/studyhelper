# Задача: Прогресс-бары по предметам

## Приоритет: P2 (средний)
## Сложность: Низкая
## Затрагивает: Backend (endpoint) + Frontend

## Описание
Визуальные прогресс-бары показывающие сколько работ сдано по каждому предмету и общий прогресс за семестр. Сравнение прогресса между двумя пользователями (pair mode).

## Зачем
Визуальная мотивация. Студент видит прогресс и понимает где отстаёт. В парном режиме — видит сравнение с партнёром.

---

## Чеклист

### Фаза 1: Backend — endpoint статистики
- [ ] Создать `GET /api/v1/stats/progress` — возвращает прогресс:
  - По каждому предмету: total_works, completed, in_progress, not_started
  - Общий по семестру: total, completed, percentage
  - Сравнение между пользователями (if pair mode)
- [ ] Создать `schemas/stats.py` (SubjectProgress, SemesterProgress, ProgressResponse)
- [ ] Создать `services/stats.py` — логика подсчёта

### Фаза 2: Frontend — компонент ProgressBar
- [ ] Создать `components/ui/progress-bar.tsx` (shadcn-style):
  - Анимированный заполняемый бар
  - Цвет: красный (0-30%), оранжевый (30-60%), зелёный (60-100%)
  - Подпись: "5 из 12 (42%)"
  - Поддержка двух значений для сравнения (pair mode)
- [ ] Создать `components/SubjectProgressCard.tsx`:
  - Название предмета
  - Прогресс-бар
  - Breakdown: X не начато, Y в работе, Z сдано

### Фаза 3: Интеграция
- [ ] На `SubjectsPage` — добавить прогресс-бар к каждому предмету
- [ ] На `DashboardPage` — виджет "Прогресс семестра" (общий бар + top-3 отстающих предмета)
- [ ] На `WorksPage` — summary bar вверху страницы
- [ ] Создать `services/statsService.ts`

### Фаза 4: Pair mode сравнение
- [ ] Двойной прогресс-бар: "Ты: 60% / Партнёр: 45%"
- [ ] Цветовое разделение (синий — ты, фиолетовый — партнёр)
- [ ] На DashboardPage — "Ты впереди на 3 работы" или "Партнёр впереди на 2 работы"

### Фаза 5: Тесты
- [ ] Backend: тесты для stats service
- [ ] Frontend: тесты для ProgressBar, SubjectProgressCard

---

## Технические детали

### API Response
```json
{
  "semester_progress": {
    "total_works": 24,
    "completed": 10,
    "in_progress": 5,
    "not_started": 9,
    "percentage": 42
  },
  "subjects": [
    {
      "subject_id": 1,
      "subject_name": "Математический анализ",
      "total_works": 8,
      "completed": 3,
      "in_progress": 2,
      "not_started": 3,
      "percentage": 38
    }
  ],
  "partner_progress": {
    "semester_percentage": 35,
    "subjects": [...]
  }
}
```

### ProgressBar компонент
```tsx
interface ProgressBarProps {
  value: number         // 0-100
  partnerValue?: number // 0-100 (pair mode)
  label?: string
  showPercentage?: boolean
  size?: 'sm' | 'md' | 'lg'
}

function getProgressColor(value: number): string {
  if (value >= 60) return 'bg-green-500'
  if (value >= 30) return 'bg-orange-500'
  return 'bg-red-500'
}
```

## Связанные файлы
- `backend/src/services/` — новый `stats.py`
- `backend/src/routers/` — новый `stats.py`
- `backend/src/schemas/` — новый `stats.py`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/SubjectsPage.tsx`
- `frontend/src/pages/WorksPage.tsx`
