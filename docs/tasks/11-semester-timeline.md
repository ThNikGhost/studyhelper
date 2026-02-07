# Задача: Учебный план семестра (Timeline)

## Приоритет: P3 (низкий)
## Сложность: Средняя
## Затрагивает: Frontend (в основном)

## Описание
Визуальный таймлайн семестра: горизонтальная полоса с контрольными точками (дедлайны, контрольные, экзамены). Текущая позиция выделена. Помогает оценить, сколько осталось до конца семестра и какие события впереди.

## Зачем
Студенты часто теряют ощущение масштаба: сколько прошло, сколько осталось, где "узкие места" с кучей дедлайнов. Timeline даёт visual overview всего семестра.

---

## Чеклист

### Фаза 1: Компонент Timeline
- [ ] Создать `components/SemesterTimeline.tsx`:
  - Горизонтальная полоса от start_date до end_date семестра
  - Маркер "Сегодня" (вертикальная линия)
  - Точки на таймлайне — дедлайны работ, контрольные, экзамены
  - Цветовая кодировка точек по типу: лабораторная (синий), контрольная (оранжевый), экзамен (красный), курсовая (фиолетовый)
  - Hover на точке → tooltip с деталями
  - Клик на точке → навигация к работе

### Фаза 2: Данные
- [ ] Использовать существующие данные: Semester (даты) + Works (дедлайны)
- [ ] Агрегация: сгруппировать близкие дедлайны (в радиусе 2 дней) чтобы не перекрывались
- [ ] Вычислить "загруженные периоды" — недели с 3+ дедлайнами (подсветить красным)

### Фаза 3: Интеграция
- [ ] Добавить Timeline на `DashboardPage` (компактная версия, одна строка)
- [ ] Добавить Timeline на `SemestersPage` (полная версия, с деталями)
- [ ] Responsive: на mobile — вертикальный таймлайн, на desktop — горизонтальный

### Фаза 4: Тесты
- [ ] Тесты для SemesterTimeline (рендер, маркеры, responsive)

---

## Технические детали

### Timeline компонент
```tsx
interface TimelineEvent {
  id: number
  date: string
  title: string
  type: 'homework' | 'lab' | 'test' | 'exam' | 'course_work'
  subject: string
  completed: boolean
}

interface SemesterTimelineProps {
  startDate: string
  endDate: string
  events: TimelineEvent[]
  compact?: boolean  // для dashboard
}

function SemesterTimeline({ startDate, endDate, events, compact }: SemesterTimelineProps) {
  const totalDays = daysBetween(startDate, endDate)
  const todayOffset = daysBetween(startDate, today()) / totalDays * 100 // percentage

  return (
    <div className="relative h-12 bg-gray-100 dark:bg-gray-800 rounded-full">
      {/* Progress bar */}
      <div className="absolute h-full bg-blue-100 rounded-full" style={{ width: `${todayOffset}%` }} />

      {/* Today marker */}
      <div className="absolute h-full w-0.5 bg-blue-600" style={{ left: `${todayOffset}%` }} />

      {/* Event dots */}
      {events.map(event => {
        const offset = daysBetween(startDate, event.date) / totalDays * 100
        return (
          <div
            key={event.id}
            className={`absolute w-3 h-3 rounded-full ${getEventColor(event.type)}`}
            style={{ left: `${offset}%`, top: '50%', transform: 'translate(-50%, -50%)' }}
            title={event.title}
          />
        )
      })}

      {/* Month labels */}
      {!compact && <MonthLabels startDate={startDate} endDate={endDate} />}
    </div>
  )
}
```

### Цвета типов работ
```typescript
const eventColors = {
  homework: 'bg-blue-500',
  lab: 'bg-cyan-500',
  test: 'bg-orange-500',
  exam: 'bg-red-500',
  course_work: 'bg-purple-500',
} as const
```

### Кластеризация
Если несколько дедлайнов ближе 2 дней друг от друга — показать как одну точку с числом:
```tsx
// Cluster: "3 дедлайна" → один кружок с цифрой 3
<div className="absolute w-6 h-6 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
  3
</div>
```

## Связанные файлы
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/SemestersPage.tsx`
- `frontend/src/services/workService.ts` — дедлайны
- `frontend/src/services/subjectService.ts` — семестры
- `frontend/src/types/work.ts`, `frontend/src/types/subject.ts`
