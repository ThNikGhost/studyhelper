# 04-dashboard-widget: Улучшение виджетов Dashboard

## Цель
Улучшить DashboardPage: показать полное расписание на сегодня (вместо только текущей/следующей пары), улучшить виджет дедлайнов с группировкой по срочности, вынести виджеты в отдельные компоненты.

## Что меняется

### 1. TodayScheduleWidget (заменяет CurrentLessonWidget)
- Показывает **все пары на сегодня** (endpoint `/schedule/today` уже есть)
- Текущая пара подсвечена (данные из `/schedule/current`)
- Прошедшие пары приглушены
- Таймер "через X мин" до следующей пары
- Пустое состояние: "Сегодня занятий нет"
- Ссылка "Полное расписание →" внизу

### 2. DeadlinesWidget (улучшенный)
- Группировка по срочности: **Просрочено** (красный) → **Сегодня/Завтра** (оранжевый) → **На неделе** (обычный)
- Badge с количеством просроченных в заголовке
- До 8 видимых элементов (вместо 5)
- Ссылка "Все работы →" внизу

### 3. QuickActions (вынесен)
- Улучшенная адаптивная сетка: `grid-cols-2 sm:grid-cols-3 lg:grid-cols-5`

### 4. Утилиты перенесены в dateUtils
- `formatTime(timeStr)` — формат HH:MM из HH:MM:SS
- `formatTimeUntil(seconds)` — "через X мин / X ч Y мин"

## Файлы

| Файл | Действие |
|------|----------|
| `frontend/src/components/dashboard/TodayScheduleWidget.tsx` | CREATE |
| `frontend/src/components/dashboard/DeadlinesWidget.tsx` | CREATE |
| `frontend/src/components/dashboard/QuickActions.tsx` | CREATE |
| `frontend/src/lib/dateUtils.ts` | MODIFY — добавить `formatTime`, `formatTimeUntil` |
| `frontend/src/pages/DashboardPage.tsx` | MODIFY — рефакторинг, подключение новых компонентов, добавление query `todaySchedule` |
| `frontend/src/test/mocks/handlers.ts` | MODIFY — добавить mock `/schedule/today` |
| `frontend/src/pages/__tests__/DashboardPage.test.tsx` | MODIFY — обновить под новую структуру |
| `frontend/src/components/dashboard/__tests__/TodayScheduleWidget.test.tsx` | CREATE |
| `frontend/src/components/dashboard/__tests__/DeadlinesWidget.test.tsx` | CREATE |
| `frontend/src/lib/__tests__/dateUtils.test.ts` | MODIFY — тесты для `formatTime`, `formatTimeUntil` |

## Data Fetching (DashboardPage)

```typescript
// Все пары на сегодня
useQuery({ queryKey: ['schedule', 'today'], queryFn: scheduleService.getTodaySchedule })

// Текущая/следующая пара (для подсветки, обновляется каждую минуту)
useQuery({ queryKey: ['currentLesson'], queryFn: scheduleService.getCurrentLesson, refetchInterval: 60000 })

// Ближайшие дедлайны
useQuery({ queryKey: ['upcomingWorks'], queryFn: workService.getUpcomingWorks(10) })
```

Бэкенд не трогаем — все endpoint'ы уже существуют.

## Порядок реализации
1. Добавить `formatTime`, `formatTimeUntil` в `dateUtils.ts` + тесты
2. Создать `TodayScheduleWidget`
3. Создать `DeadlinesWidget`
4. Создать `QuickActions`
5. Рефакторинг `DashboardPage` — заменить inline-виджеты на импорты
6. Обновить MSW handlers + тесты
7. Проверить ESLint, TypeScript, build

## Верификация
```bash
cd frontend && npx vitest run          # все тесты проходят
cd frontend && npm run lint            # ESLint чисто
cd frontend && npm run build           # TypeScript + Vite build
```
