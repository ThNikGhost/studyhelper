# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит (2026-03-02): fix(frontend): fix deadline off-by-one, PE stats, and dashboard 7-day filter (b4348b2).

### Что сделано в этой сессии (2026-03-02):
- **Bug 1 — Attendance PE stats:** `filteredStats` теперь пересчитывает строку по физкультуре из `filteredEntries` (уже отфильтрованных по `peTeacher`). `filteredEntries` перенесён перед `filteredStats`. Условие short-circuit изменено: `!settings.peTeacher && fullyHiddenIds.size === 0`. При `filterSubjectId === null` и активном `peTeacher` — пересчитывает `total_classes/absences/attended/attendance_percent` по физкультуре из записей журнала.
- **Bug 2 — Deadline off-by-one:** `formatDeadline` и `getDeadlineColor` в `dateUtils.ts` используют calendar-day сравнение (`new Date(y, m, d)`) вместо `Math.ceil(diffMs/24h)`. Дедлайн сегодня в 23:59 при просмотре в 08:00 → "Сегодня" (было "Завтра"). +2 регрессионных теста.
- **Bug 3 — Dashboard 7-day filter:** `getUrgency` в `DeadlinesWidget` возвращает `null` при `diffDays > 7`. Нули фильтруются перед группировкой. Тест "shows max 8 items" переписан с fake timers (3 overdue + 7 within 7 days = 10, обрезается до 8). Добавлен тест "does not show works with deadline beyond 7 days".

## Следующие шаги (по приоритету)
- Задеплоить b4348b2 на prod (если нужно — `git pull && docker compose -f docker-compose.prod.yml up -d --build backend`)
- (Фаза 3) httpOnly cookies — access token в памяти, refresh в httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет

## Известные pre-existing падения тестов
- `SchedulePage.test.tsx` — 3 теста падают (hidden subjects filter применяется в mock-данных)
- Не связаны с текущими изменениями, существуют с момента добавления фильтрации расписания
