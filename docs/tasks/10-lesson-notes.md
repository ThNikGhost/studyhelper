# Задача: Заметки к парам

## Приоритет: P2 (средний)
## Сложность: Средняя
## Затрагивает: Backend + Frontend

## Описание
Быстрые текстовые заметки, привязанные к конкретной паре (дата + предмет). "На следующей паре будет контрольная", "Принести тетрадь", "Домашка: стр. 45, задачи 1-10".

## Зачем
Студенты записывают заметки в телефон, на бумажке, в мессенджере — потом теряют. Заметки привязанные к парам в расписании — контекстно удобно.

---

## Чеклист

### Фаза 1: Backend — модель и API
- [ ] Создать модель `LessonNote`:
  - `id`, `user_id`, `schedule_entry_id` (nullable), `subject_name`, `lesson_date`, `content` (text), `created_at`, `updated_at`
  - Привязка к schedule_entry_id если есть, иначе по subject_name + lesson_date
- [ ] Alembic миграция
- [ ] Создать `schemas/lesson_note.py`
- [ ] Создать `services/lesson_note.py`:
  - `create_note(db, user_id, data)` — создать
  - `update_note(db, note_id, user_id, content)` — обновить
  - `delete_note(db, note_id, user_id)` — удалить
  - `get_notes_by_date(db, user_id, date)` — заметки за день
  - `get_notes_by_subject(db, user_id, subject_name)` — заметки по предмету
  - `search_notes(db, user_id, query)` — поиск по тексту
- [ ] Создать `routers/lesson_notes.py`:
  - `POST /api/v1/notes`
  - `GET /api/v1/notes?date=...&subject=...&search=...`
  - `PUT /api/v1/notes/{id}`
  - `DELETE /api/v1/notes/{id}`

### Фаза 2: Frontend — компоненты
- [ ] Создать `components/NoteEditor.tsx`:
  - Простое текстовое поле (textarea)
  - Автосохранение через debounce (500ms)
  - Показать статус: "Сохранено" / "Сохранение..."
  - Markdown поддержка (опционально, в будущем)
- [ ] Создать `services/noteService.ts`

### Фаза 3: Интеграция в расписание
- [ ] В `LessonDetailModal` (из задачи 06) — секция "Заметки":
  - Показать существующие заметки к этой паре
  - Кнопка "Добавить заметку" → inline editor
  - Редактирование/удаление существующих
- [ ] В `LessonCard` — маленькая иконка 📝 если есть заметки к этой паре
- [ ] В `DayScheduleCard` — индикатор количества заметок

### Фаза 4: Отдельный вид заметок
- [ ] Создать `NotesPage.tsx` или секцию на DashboardPage:
  - Все заметки за текущую неделю
  - Фильтрация по предмету
  - Поиск по тексту
  - Сортировка по дате (новые первые)
- [ ] Добавить маршрут `/notes` в `App.tsx` (опционально)

### Фаза 5: Тесты
- [ ] Backend: тесты для note service (CRUD, поиск, фильтрация)
- [ ] Backend: тесты для API endpoints
- [ ] Frontend: тесты для NoteEditor (создание, автосохранение)

---

## Технические детали

### Модель БД
```python
class LessonNote(Base):
    __tablename__ = 'lesson_notes'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    schedule_entry_id: Mapped[int | None] = mapped_column(ForeignKey('schedule_entries.id'), nullable=True)
    subject_name: Mapped[str] = mapped_column(String(200))
    lesson_date: Mapped[date]
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('ix_lesson_notes_user_date', 'user_id', 'lesson_date'),
        Index('ix_lesson_notes_user_subject', 'user_id', 'subject_name'),
    )
```

### Автосохранение
```typescript
// Debounced auto-save
const saveNote = useMutation({
  mutationFn: (content: string) => noteService.update(noteId, content),
})

const debouncedSave = useMemo(
  () => debounce((content: string) => saveNote.mutate(content), 500),
  [noteId]
)

const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  setContent(e.target.value)
  debouncedSave(e.target.value)
}
```

### UX
- Максимальная длина заметки: 2000 символов
- Placeholder: "Заметка к паре..."
- Минимальная высота textarea: 3 строки, auto-expand
- Отображение: компактные карточки с датой и первой строкой заметки

## Связанные файлы
- `backend/src/models/` — новая модель
- `backend/src/services/` — новый сервис
- `backend/src/routers/` — новый роутер
- `frontend/src/components/schedule/LessonCard.tsx` — иконка заметки
- `frontend/src/components/schedule/` — LessonDetailModal (из задачи 06)
