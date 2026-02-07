# Задача: Экспорт расписания в .ics

## Приоритет: P2 (средний)
## Сложность: Низкая
## Затрагивает: Backend + Frontend (минимально)

## Описание
Экспорт расписания и дедлайнов в формат iCalendar (.ics) для импорта в Google Calendar, Apple Calendar, Outlook.

## Зачем
Многие студенты используют Google/Apple Calendar. Возможность импортировать расписание одной кнопкой — большое удобство. Реализация простая, польза большая.

---

## Чеклист

### Фаза 1: Backend — генерация .ics
- [ ] Добавить зависимость `icalendar` в `pyproject.toml`
- [ ] Создать `services/ical.py`:
  - `generate_schedule_ics(entries: list[ScheduleEntry]) -> bytes` — расписание
  - `generate_deadlines_ics(works: list[Work]) -> bytes` — дедлайны
  - `generate_combined_ics(entries, works) -> bytes` — всё вместе
- [ ] Правильная обработка timezone (Asia/Omsk, UTC+6)
- [ ] VEVENT для каждой пары: summary, location (room + building), description (teacher, type), dtstart/dtend
- [ ] VEVENT для дедлайнов: summary, description (subject, type), VALARM за 1 день

### Фаза 2: Backend — API endpoints
- [ ] `GET /api/v1/export/schedule.ics?from=2026-02-01&to=2026-06-30` — расписание
- [ ] `GET /api/v1/export/deadlines.ics` — дедлайны текущего семестра
- [ ] `GET /api/v1/export/all.ics` — расписание + дедлайны
- [ ] Response headers: `Content-Type: text/calendar`, `Content-Disposition: attachment`
- [ ] Аутентификация через query parameter `?token=...` (JWT не работает с прямым скачиванием)

### Фаза 3: Frontend — кнопки экспорта
- [ ] На `SchedulePage` — кнопка "Экспорт в календарь" (иконка calendar-download)
- [ ] На `WorksPage` — кнопка "Экспорт дедлайнов"
- [ ] Модалка с опциями: "Расписание", "Дедлайны", "Всё вместе"
- [ ] Скачивание файла через `<a download>` или `window.open`

### Фаза 4: Тесты
- [ ] Backend: тесты генерации .ics (корректность формата, timezone, VALARM)
- [ ] Backend: тесты для endpoints

---

## Технические детали

### Формат .ics
```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//StudyHelper//Schedule//RU
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Расписание ОмГУ
X-WR-TIMEZONE:Asia/Omsk
BEGIN:VEVENT
DTSTART:20260210T083000
DTEND:20260210T100000
SUMMARY:Математический анализ (лекция)
LOCATION:ауд. 310, корпус 1
DESCRIPTION:Преподаватель: Иванов И.И.
END:VEVENT
...
END:VCALENDAR
```

### Дедлайн как VEVENT + напоминание
```
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260215
SUMMARY:Дедлайн: Лабораторная №3 по Физике
DESCRIPTION:Тип: лабораторная работа\nПредмет: Физика
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Завтра дедлайн!
END:VALARM
END:VEVENT
```

### Auth для скачивания
```python
# Генерация короткоживущего токена для скачивания
@router.get('/export/schedule.ics')
async def export_schedule(
    token: str = Query(...),  # одноразовый токен
    db: AsyncSession = Depends(get_db),
):
    user = await verify_download_token(token, db)
    entries = await schedule_service.get_all(db)
    ics_data = generate_schedule_ics(entries)
    return Response(content=ics_data, media_type='text/calendar',
                    headers={'Content-Disposition': 'attachment; filename=schedule.ics'})
```

## Связанные файлы
- `backend/src/services/` — новый `ical.py`
- `backend/src/routers/` — новый `export.py`
- `frontend/src/pages/SchedulePage.tsx`
- `frontend/src/pages/WorksPage.tsx`
