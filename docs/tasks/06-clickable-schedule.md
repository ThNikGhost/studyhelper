# Задача: Кликабельные элементы расписания

## Приоритет: P1 (высокий)
## Сложность: Низкая
## Затрагивает: Frontend

## Описание
Сделать элементы расписания интерактивными: клик на предмет, преподавателя, аудиторию раскрывает дополнительную информацию и ведёт к связанным данным.

## Зачем
Расписание — самая используемая страница. Кликабельные элементы превращают его из статичной таблицы в навигационный хаб.

---

## Чеклист

### Фаза 1: LessonCard → кликабельная карточка
- [ ] Обернуть `LessonCard` в кликабельный контейнер
- [ ] По клику — открыть детальную модалку `LessonDetailModal`:
  - Предмет (полное название) — ссылка на SubjectsPage с фильтром
  - Преподаватель (ФИО, должность, кафедра) — если есть в БД
  - Аудитория + корпус
  - Тип пары (лекция/практика/лабораторная)
  - Время (начало — конец)
  - Связанные работы по этому предмету (ближайшие дедлайны)
- [ ] Hover-эффект на LessonCard для индикации кликабельности
- [ ] Keyboard accessible: Enter/Space для открытия

### Фаза 2: Быстрые действия в модалке
- [ ] Кнопка "Все работы по предмету" → `/works?subject={id}`
- [ ] Кнопка "Добавить работу" → модалка создания работы с предзаполненным предметом
- [ ] Кнопка "Информация о преподавателе" → модалка с данными преподавателя (если есть teacher_id)

### Фаза 3: Связывание с данными
- [ ] Определить `subject_id` по `subject_name` из расписания (fuzzy match или точное совпадение)
- [ ] Определить `teacher_id` по `teacher_name` из расписания
- [ ] Если совпадение найдено — показать данные, если нет — показать только текст

### Фаза 4: Тесты
- [ ] Тесты для LessonDetailModal (рендер, связанные данные, пустые состояния)
- [ ] Тесты для кликабельности LessonCard

---

## Технические детали

### LessonDetailModal
```tsx
interface LessonDetailModalProps {
  lesson: ScheduleEntry
  isOpen: boolean
  onClose: () => void
}

function LessonDetailModal({ lesson, isOpen, onClose }: LessonDetailModalProps) {
  // Загрузить связанные данные
  const { data: subject } = useQuery({
    queryKey: ['subject-by-name', lesson.subject_name],
    queryFn: () => subjectService.getByName(lesson.subject_name),
    enabled: isOpen,
  })

  const { data: works } = useQuery({
    queryKey: ['works-by-subject', subject?.id],
    queryFn: () => workService.getBySubject(subject!.id),
    enabled: !!subject?.id,
  })

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={lesson.subject_name}>
      <div>Тип: {lesson.lesson_type}</div>
      <div>Время: {lesson.start_time} — {lesson.end_time}</div>
      <div>Аудитория: {lesson.room}, {lesson.building}</div>
      <div>Преподаватель: {lesson.teacher_name}</div>
      {works?.length > 0 && (
        <div>
          <h4>Ближайшие работы:</h4>
          {works.map(w => <WorkCard key={w.id} work={w} />)}
        </div>
      )}
    </Modal>
  )
}
```

### Backend доработки
Возможно нужен endpoint:
- `GET /api/v1/subjects/by-name?name=...` — поиск предмета по имени
Или сопоставление можно делать на фронте по загруженному списку предметов.

### UX
- На mobile: модалка занимает весь экран (bottom sheet)
- На desktop: центрированная модалка средних размеров
- Плавный hover: `transition-colors duration-150, bg-gray-50 on hover`

## Связанные файлы
- `frontend/src/components/schedule/LessonCard.tsx`
- `frontend/src/components/schedule/ScheduleGrid.tsx`
- `frontend/src/components/schedule/DayScheduleCard.tsx`
- `frontend/src/components/ui/modal.tsx`
- `frontend/src/services/workService.ts`
- `frontend/src/services/subjectService.ts`
