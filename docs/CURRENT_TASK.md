# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит (2026-02-23): fix(attendance): apply partial hidden subjects and PE teacher filter to journal (d0ef93b).

### Что сделано в этой сессии (2026-02-23):
- AttendancePage: `filteredEntries` теперь фильтрует журнал по трём условиям:
  1. Полностью скрытый предмет (`hiddenTypes === null`)
  2. Частично скрытый тип занятия (`hiddenTypes.includes(e.lesson_type)`)
  3. Несовпадение преподавателя физкультуры (`peTeacher` ≠ `teacher_name`)
- Логика зеркалит `schedule_filters.py` на Python
- FileList.test.tsx: добавлена обёртка `QueryClientProvider` — тест падал т.к. `FileList` использует `useQueryClient()`
- Все 16 тестов затронутых файлов прошли
- Задеплоено через CI/CD на https://studyhelper1.ru (d0ef93b на сервере)

## Следующие шаги (по приоритету)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет

## Известные pre-existing падения тестов
- `SchedulePage.test.tsx` — 3 теста падают (hidden subjects filter применяется в mock-данных)
- Не связаны с текущими изменениями, существуют с момента добавления фильтрации расписания
