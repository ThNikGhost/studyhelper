# Текущая задача

## Задача
SubjectsPage frontend (незавершённый коммит)

## Описание
SubjectsPage создана, но сессия прервалась до проверки сборки и коммита.

## Критерии готовности
- [x] Создать types/subject.ts
- [x] Создать services/subjectService.ts
- [x] Создать pages/SubjectsPage.tsx
- [x] Обновить App.tsx
- [ ] Проверить сборку frontend (npm run build)
- [ ] Закоммитить изменения

## Прогресс
- [x] TypeScript типы (Subject, Semester, SubjectCreate, etc.)
- [x] Сервис API (CRUD для subjects и semesters)
- [x] Страница с фильтрацией по семестру
- [x] Модалки для добавления/редактирования/удаления
- [ ] Проверка сборки
- [ ] Коммит

## Заметки по реализации
SubjectsPage включает:
- Выбор семестра (dropdown)
- Список предметов карточками
- Кнопки редактирования и удаления
- Модальное окно для добавления/редактирования
- Модальное окно подтверждения удаления
- Пустое состояние
- Кнопка "назад" на главную

## Созданные файлы (не закоммичены)
- `frontend/src/types/subject.ts`
- `frontend/src/services/subjectService.ts`
- `frontend/src/pages/SubjectsPage.tsx`
- `frontend/src/App.tsx` (изменён)

## Следующие задачи
1. Проверить `npm run build` во frontend
2. Закоммитить SubjectsPage
3. Создать WorksPage
4. Создать ClassmatesPage

## Блокеры / Вопросы
Нет блокеров.
