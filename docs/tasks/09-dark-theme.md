# Задача: Тёмная тема

## Приоритет: P2 (средний)
## Сложность: Низкая
## Затрагивает: Frontend

## Описание
Поддержка тёмной темы с автоопределением системных настроек и ручным переключением. Tailwind CSS v4 + shadcn/ui делают это относительно просто.

## Зачем
Студенты часто пользуются приложением вечером/ночью. Тёмная тема снижает нагрузку на глаза. Это также стандарт для современных приложений.

---

## Чеклист

### Фаза 1: Инфраструктура темы
- [ ] Настроить Tailwind CSS v4 dark mode (`@media (prefers-color-scheme: dark)` или class-based)
- [ ] Выбрать подход: **class-based** (рекомендуется) — для ручного переключения
- [ ] Создать `stores/themeStore.ts` (Zustand):
  - `theme: 'light' | 'dark' | 'system'`
  - `setTheme(theme)`
  - Persistence в localStorage
  - На старте: определить текущую тему по system preference
- [ ] Добавить/убрать класс `dark` на `<html>` при смене темы

### Фаза 2: CSS переменные для тёмной темы
- [ ] Определить палитру для dark mode в `index.css`:
  - Background: `#0f172a` (slate-900)
  - Surface: `#1e293b` (slate-800)
  - Text: `#f1f5f9` (slate-100)
  - Border: `#334155` (slate-700)
  - Primary: оставить или сделать чуть ярче
- [ ] shadcn/ui компоненты уже поддерживают dark mode (проверить)
- [ ] Обновить кастомные компоненты (Modal, custom cards)

### Фаза 3: Переключатель темы
- [ ] Создать `components/ThemeToggle.tsx`:
  - Иконка: ☀️ / 🌙 / 💻 (light / dark / system)
  - Dropdown с тремя опциями
  - Плавная анимация перехода
- [ ] Разместить в header (рядом с именем пользователя)
- [ ] Сохранение выбора в localStorage

### Фаза 4: Адаптация всех страниц
- [ ] Проверить и исправить каждую страницу:
  - [ ] LoginPage / RegisterPage
  - [ ] DashboardPage
  - [ ] SchedulePage (LessonCard, DayScheduleCard, ScheduleGrid)
  - [ ] SubjectsPage
  - [ ] WorksPage
  - [ ] SemestersPage
  - [ ] ClassmatesPage
- [ ] Проверить модалки (Modal)
- [ ] Проверить toast-уведомления (sonner)
- [ ] Проверить календарь (react-day-picker)

### Фаза 5: Тесты
- [ ] Тесты для themeStore (переключение, persistence, system detection)
- [ ] Тесты для ThemeToggle (рендер, клик, иконки)
- [ ] Визуальная проверка всех страниц в обеих темах

---

## Технические детали

### Tailwind CSS v4 dark mode
```css
/* index.css */
@custom-variant dark (&:where(.dark, .dark *));

:root {
  --background: #ffffff;
  --foreground: #0f172a;
  --card: #ffffff;
  --card-foreground: #0f172a;
  --border: #e2e8f0;
}

.dark {
  --background: #0f172a;
  --foreground: #f1f5f9;
  --card: #1e293b;
  --card-foreground: #f1f5f9;
  --border: #334155;
}
```

### Theme Store
```typescript
interface ThemeState {
  theme: 'light' | 'dark' | 'system'
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark' | 'system') => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'system',
      resolvedTheme: getSystemTheme(),
      setTheme: (theme) => {
        const resolved = theme === 'system' ? getSystemTheme() : theme
        document.documentElement.classList.toggle('dark', resolved === 'dark')
        set({ theme, resolvedTheme: resolved })
      },
    }),
    { name: 'theme-storage' }
  )
)

function getSystemTheme(): 'light' | 'dark' {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}
```

### ThemeToggle
```tsx
function ThemeToggle() {
  const { theme, setTheme } = useThemeStore()
  const icons = { light: <Sun />, dark: <Moon />, system: <Monitor /> }

  return (
    <button onClick={() => {
      const next = { light: 'dark', dark: 'system', system: 'light' } as const
      setTheme(next[theme])
    }}>
      {icons[theme]}
    </button>
  )
}
```

### Что уже поддерживает dark mode
- shadcn/ui Button, Input, Card, Label — ✅ (если CSS-переменные настроены)
- sonner toasts — ✅ (есть prop `theme`)
- react-day-picker — нужно проверить, может потребоваться кастомизация

## Связанные файлы
- `frontend/src/index.css` — CSS-переменные
- `frontend/src/stores/` — новый `themeStore.ts`
- `frontend/src/components/` — новый `ThemeToggle.tsx`
- `frontend/src/pages/` — все страницы (проверка)
- `frontend/src/components/ui/` — shadcn компоненты
