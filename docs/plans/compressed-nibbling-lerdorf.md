# План: Frontend тесты для StudyHelper

## Обзор

Добавить тестовую инфраструктуру и unit-тесты для frontend. Сейчас тестов нет вообще — ни фреймворка, ни файлов.

**Стек**: Vitest + @testing-library/react + jsdom + msw (mock API)

---

## Фаза 0: Инфраструктура

### 0.1 Установить зависимости

```bash
cd frontend && npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom msw
```

### 0.2 Конфигурация Vitest

Добавить `test` конфиг в `vite.config.ts`:

```ts
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: './src/test/setup.ts',
  css: false,
}
```

### 0.3 Setup файл

`frontend/src/test/setup.ts`:
- Import `@testing-library/jest-dom/vitest`
- Mock `localStorage`
- Mock `window.matchMedia`
- Настроить MSW server (beforeAll/afterEach/afterAll)

### 0.4 MSW handlers

`frontend/src/test/mocks/handlers.ts`:
- Заглушки для основных API endpoints (auth, subjects, semesters)
- Фабрики тестовых данных

### 0.5 package.json

Добавить скрипт: `"test": "vitest"`

**Файлы**: `vite.config.ts`, `src/test/setup.ts` (новый), `src/test/mocks/handlers.ts` (новый), `src/test/mocks/server.ts` (новый), `package.json`

---

## Фаза 1: Тесты утилит (чистые функции — без моков)

### 1.1 `src/lib/__tests__/dateUtils.test.ts`

Тесты для `formatDeadline`:
- Просрочено (дата в прошлом) → "Просрочено"
- Сегодня → "Сегодня"
- Завтра → "Завтра"
- Через 5 дней → "Через 5 дн."
- Через 14 дней → дата в формате "1 мар."

Тесты для `getDeadlineColor`:
- Просрочено → red
- Сегодня/завтра → orange
- Через 2-3 дня → yellow
- Через 7+ дней → muted

Тесты для `formatDateLocal`:
- Форматирует Date → "YYYY-MM-DD"
- Padding для одноцифровых месяцев/дней
- Без UTC сдвига (именно local)

Тесты для `getToday`:
- Возвращает строку формата YYYY-MM-DD

### 1.2 `src/lib/__tests__/errorUtils.test.ts`

Тесты для `getErrorMessage`:
- AxiosError с detail string → возвращает detail
- AxiosError с 401 статусом → "Неверный email или пароль"
- AxiosError с 429 → "Слишком много запросов..."
- AxiosError ERR_NETWORK → "Ошибка сети..."
- Обычный Error → error.message
- Неизвестная ошибка → fallback
- Без аргумента fallback → "Произошла ошибка"

### 1.3 `src/lib/__tests__/constants.test.ts`

- TIME_SLOTS содержит 8 пар
- Формат start/end: HH:MM
- LESSON_TYPE_COLORS имеет все типы из LessonType

**Файлы**: 3 новых тест-файла в `src/lib/__tests__/`

---

## Фаза 2: Тесты Store

### 2.1 `src/stores/__tests__/authStore.test.ts`

Тесты для `useAuthStore`:
- Начальное состояние: user=null, isAuthenticated зависит от localStorage
- `login()`: сохраняет токены, делает fetchUser, устанавливает isAuthenticated
- `login()` ошибка: не меняет isAuthenticated, isLoading сбрасывается
- `logout()`: очищает токены, сбрасывает state
- `fetchUser()`: без токена — сбрасывает state
- `fetchUser()`: с токеном — загружает user
- `setUser(null)`: сбрасывает isAuthenticated

MSW для моков: `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`

**Файлы**: `src/stores/__tests__/authStore.test.ts`

---

## Фаза 3: Тесты компонентов

### 3.1 `src/components/__tests__/ProtectedRoute.test.tsx`

- Авторизованный пользователь → рендерит children
- Неавторизованный → редирект на /login

### 3.2 `src/components/__tests__/ErrorBoundary.test.tsx`

- Без ошибки → рендерит children
- С ошибкой → показывает fallback UI

### 3.3 `src/components/ui/__tests__/modal.test.tsx`

- isOpen=false → не рендерится
- isOpen=true → рендерит title и children
- Клик на backdrop → вызывает onClose
- Нажатие Escape → вызывает onClose
- aria-modal и role="dialog" присутствуют

**Файлы**: 3 новых тест-файла в `src/components/__tests__/` и `src/components/ui/__tests__/`

---

## Фаза 4: Тесты страниц (интеграционные)

### 4.1 `src/pages/__tests__/LoginPage.test.tsx`

- Рендерит форму (email, password, кнопка)
- Заполнение и submit → вызывает login
- Ошибка login → показывает сообщение
- Ссылка на регистрацию существует

### 4.2 `src/pages/__tests__/DashboardPage.test.tsx`

- Loading state → показывает skeleton
- Error state → показывает ошибку
- Success → рендерит виджеты
- Навигационные ссылки присутствуют

**Файлы**: 2 новых тест-файла в `src/pages/__tests__/`

---

## Сводка файлов

| Файл | Тип |
|------|-----|
| `frontend/package.json` | Изменить (зависимости + скрипт) |
| `frontend/vite.config.ts` | Изменить (test config) |
| `frontend/src/test/setup.ts` | Новый |
| `frontend/src/test/mocks/handlers.ts` | Новый |
| `frontend/src/test/mocks/server.ts` | Новый |
| `frontend/src/lib/__tests__/dateUtils.test.ts` | Новый |
| `frontend/src/lib/__tests__/errorUtils.test.ts` | Новый |
| `frontend/src/lib/__tests__/constants.test.ts` | Новый |
| `frontend/src/stores/__tests__/authStore.test.ts` | Новый |
| `frontend/src/components/__tests__/ProtectedRoute.test.tsx` | Новый |
| `frontend/src/components/__tests__/ErrorBoundary.test.tsx` | Новый |
| `frontend/src/components/ui/__tests__/modal.test.tsx` | Новый |
| `frontend/src/pages/__tests__/LoginPage.test.tsx` | Новый |
| `frontend/src/pages/__tests__/DashboardPage.test.tsx` | Новый |

**Итого**: 12 новых тест-файлов, 2 изменённых конфига

---

## Верификация

```bash
cd frontend && npm run test -- --run
```

Ожидаемый результат: все тесты проходят, ~40-50 тестов.
