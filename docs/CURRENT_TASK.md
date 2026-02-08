# Текущая задача

## Статус
**10-lesson-notes завершена** — реализована на ветке `main`, ожидает коммит.

## Выполнено: 10-lesson-notes (заметки к парам)

### Backend
- [x] `models/note.py` — модель LessonNote (id, user_id FK, schedule_entry_id FK nullable, subject_name, lesson_date, content Text, timestamps)
- [x] `models/__init__.py` — LessonNote в импорты
- [x] `schemas/note.py` — LessonNoteCreate, LessonNoteUpdate, LessonNoteResponse
- [x] `services/note.py` — create_note, update_note, delete_note, get_notes (filters: date_from, date_to, subject_name, search), get_note_for_entry
- [x] `routers/notes.py` — POST / (201), GET / (list with filters), GET /entry/{schedule_entry_id}, PUT /{note_id}, DELETE /{note_id} (204)
- [x] `main.py` — notes router (prefix="/notes", tags=["Notes"])
- [x] Alembic миграция add_lesson_notes_table (d62cab669757)
- [x] 21 backend тестов (create: 6, get_notes: 5, get_note_for_entry: 3, update: 4, delete: 3)

### Frontend
- [x] `types/note.ts` — LessonNote, LessonNoteCreate, LessonNoteUpdate
- [x] `services/noteService.ts` — getNotes, getNoteForEntry (404→null), createNote, updateNote, deleteNote
- [x] `components/notes/NoteEditor.tsx` — autosave debounce 500ms, status indicators (idle/saving/saved/error), char counter 2000
- [x] `components/notes/NoteCard.tsx` — subject/date, content preview 150 chars, expand/collapse, delete
- [x] `pages/NotesPage.tsx` — search debounce 300ms, subject filter, NoteCard list, delete confirmation, loading/error/empty states
- [x] `components/schedule/LessonDetailModal.tsx` — рефакторинг: textarea+save → NoteEditor с autosave через useQuery
- [x] `components/schedule/LessonCard.tsx` — hasNote prop, StickyNote icon (amber-500)
- [x] `components/schedule/ScheduleGrid.tsx` — noteEntryIds prop
- [x] `components/schedule/DayScheduleCard.tsx` — noteEntryIds prop
- [x] `pages/SchedulePage.tsx` — notes query for current week, noteEntryIds Set
- [x] `App.tsx` — маршрут /notes (ProtectedRoute + AppLayout)
- [x] `QuickActions.tsx` — пункт "Заметки" (StickyNote, text-yellow-500)
- [x] MSW handlers: GET/POST/PUT/DELETE notes, GET notes/entry/:id + testLessonNotes data
- [x] 23 новых frontend теста (NoteEditor: 10, NoteCard: 5, NotesPage: 8)
- [x] LessonDetailModal тесты обновлены (17 тестов — new NoteEditor-based behavior)
- [x] TypeScript, ESLint, build — всё чисто

## Следующие задачи (приоритет)
1. **09-dark-theme** — тёмная тема (P2)
2. **05-ics-export** — экспорт в .ics (P2)
3. **02-push-notifications** — push-уведомления (P1, зависит от PWA)
4. **11-semester-timeline** — timeline семестра (P3)

## Заметки
- Backend: 328 тестов проходят (307 + 21 новых)
- Frontend: 279 тестов проходят (258 - 2 удалённых + 23 новых)
- Все линтеры чисты
- Архитектура: одна заметка на entry на пользователя (UniqueConstraint)
- LessonDetailModal: textarea+save заменён на NoteEditor с autosave
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
