# Текущая задача

## Статус
**09-dark-theme завершена** — реализована, ожидает коммит.

## Выполнено: 09-dark-theme (тёмная тема)

### Инфраструктура
- [x] `lib/theme.ts` — ThemeMode, getSavedTheme, saveTheme, resolveTheme, applyTheme
- [x] `hooks/useTheme.ts` — React hook (mode, resolvedTheme, setTheme), system listener
- [x] `index.html` — inline FOUC prevention script, dark fallback styles

### UI
- [x] `components/ThemeToggle.tsx` — cycling button (Sun → Moon → Monitor), aria-label
- [x] `components/AppLayout.tsx` — ThemeToggle в fixed bottom-right
- [x] `main.tsx` — theme="system" на Toaster (sonner)

### Фикс hardcoded цветов
- [x] `lib/attendanceUtils.ts` — text-*-600 → + dark:text-*-400
- [x] `components/attendance/AttendanceStatsCard.tsx` — text-red-600 → + dark:text-red-400
- [x] `components/attendance/AttendanceTable.tsx` — bg-red-50 → + dark:bg-red-950/30

### Offline
- [x] `public/offline.html` — @media (prefers-color-scheme: dark)

### Тесты (30 новых)
- [x] `lib/__tests__/theme.test.ts` — 14 тестов (getSavedTheme, saveTheme, resolveTheme, applyTheme)
- [x] `hooks/__tests__/useTheme.test.ts` — 6 тестов (init, setTheme, persistence, dark class, resolved)
- [x] `components/__tests__/ThemeToggle.test.tsx` — 6 тестов (render, cycling, aria-label, dark class)
- [x] `components/__tests__/AppLayout.test.tsx` — +1 тест (renders ThemeToggle)
- [x] `lib/__tests__/attendanceUtils.test.ts` — обновлены 3 теста (dark: варианты)
- [x] TypeScript, ESLint, build — всё чисто

## Следующие задачи (приоритет)
1. **05-ics-export** — экспорт в .ics (P2)
2. **02-push-notifications** — push-уведомления (P1, зависит от PWA)

## Заметки
- Backend: 337 тестов (без изменений)
- Frontend: 351 тестов (321 + 30 новых)
- FOUC prevention: inline script до CSS, читает localStorage
- Cycling toggle: light → dark → system → light
- CSS-переменные .dark уже были в index.css (shadcn/ui)
- 500-level цвета не тронуты — видимы на обоих фонах
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
