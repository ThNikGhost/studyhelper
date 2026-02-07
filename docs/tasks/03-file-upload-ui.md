# Задача: UI загрузки файлов

## Приоритет: P1 (высокий)
## Сложность: Средняя
## Затрагивает: Frontend (backend endpoint уже есть)

## Описание
Реализовать UI для загрузки и просмотра файлов. Backend endpoint `POST /api/v1/uploads` уже существует с валидацией (magic bytes, size limit, path traversal protection). Нужен frontend.

## Зачем
Студенты хранят методички, задания, лекции в разных местах. Единое хранилище привязанное к предметам — удобно.

---

## Чеклист

### Фаза 1: Типы и сервис
- [ ] Расширить `types/` — добавить `upload.ts` (FileUpload, FileCategory)
- [ ] Расширить `services/uploadService.ts`:
  - `uploadFile(file, subjectId?, category?)` — загрузка
  - `getFiles(subjectId?)` — список файлов
  - `deleteFile(fileId)` — удаление
  - `getDownloadUrl(fileId)` — URL для скачивания
- [ ] Backend: добавить GET /api/v1/uploads (список), DELETE /api/v1/uploads/{id}, GET /api/v1/uploads/{id}/download (если нет)

### Фаза 2: Компонент загрузки (Dropzone)
- [ ] Создать `components/FileDropzone.tsx`:
  - Drag & drop зона
  - Кнопка "Выбрать файл" как fallback
  - Превью имени файла и размера перед загрузкой
  - Прогресс-бар загрузки (axios onUploadProgress)
  - Валидация на фронте: допустимые типы (pdf, doc, docx, xls, xlsx, ppt, pptx, jpg, png), максимальный размер
  - Множественная загрузка (одна за одной)
- [ ] Категории файлов: методичка, задачник, лекция, лабораторная, шпаргалка, прочее

### Фаза 3: Список файлов
- [ ] Создать `components/FileList.tsx`:
  - Таблица/список файлов (имя, категория, размер, дата, предмет)
  - Иконки по типу файла (PDF, Word, Excel, Image)
  - Кнопки: скачать, удалить (с подтверждением)
  - Фильтрация по предмету и категории
  - Сортировка по дате/имени/размеру
- [ ] Встраиваемый просмотр для PDF и изображений (modal или новая вкладка)

### Фаза 4: Интеграция в страницы
- [ ] Создать `FilesPage.tsx` — отдельная страница файлов
- [ ] Добавить маршрут `/files` в `App.tsx`
- [ ] Добавить кнопку "Файлы" в DashboardPage (Quick Actions)
- [ ] На `SubjectsPage` — показать количество файлов у предмета, ссылка на файлы предмета
- [ ] Навигация: добавить "Файлы" в основное меню (если будет sidebar/bottom nav)

### Фаза 5: Тесты
- [ ] Тесты для FileDropzone (drag & drop, валидация, upload)
- [ ] Тесты для FileList (рендер, фильтрация, удаление)

---

## Технические детали

### Типы
```typescript
type FileCategory = 'textbook' | 'problem_set' | 'lecture' | 'lab' | 'cheatsheet' | 'other'

interface FileUpload {
  id: number
  filename: string
  original_filename: string
  file_size: number
  mime_type: string
  category: FileCategory
  subject_id: number | null
  subject_name?: string
  uploaded_by: number
  created_at: string
}
```

### Backend доработки
Проверить, есть ли на backend:
- `GET /api/v1/uploads` — список файлов пользователя
- `GET /api/v1/uploads/{id}/download` — скачивание
- `DELETE /api/v1/uploads/{id}` — удаление
- Поля `category`, `subject_id` в модели Upload

Если нет — добавить.

### Drag & Drop
```typescript
// Нативный HTML5 Drag & Drop (без лишних библиотек)
const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
}
const handleDrop = (e: React.DragEvent) => {
  e.preventDefault()
  const files = Array.from(e.dataTransfer.files)
  // validate & upload
}
```

### Лимиты
- Максимальный размер файла: 50 MB (уже на backend)
- Допустимые MIME-типы: pdf, doc/docx, xls/xlsx, ppt/pptx, jpg/png/gif
- Общий лимит хранилища: 500 MB на пользователя (будущее)

## Связанные файлы
- `frontend/src/services/uploadService.ts` — уже существует
- `backend/src/services/upload.py` — уже существует
- `backend/src/routers/uploads.py` — уже существует
- `backend/src/models/` — возможно нужна модель Upload
