# Архитектурные решения

## Дата создания: 2026-02-03

---

## 1. Выбор фреймворков

### Frontend: React + TypeScript + Vite

**Решение:** Использовать React с TypeScript и сборщиком Vite.

**Обоснование:**
- Vite обеспечивает быструю сборку и HMR (Hot Module Replacement)
- React — самая популярная библиотека с огромным сообществом
- TypeScript даёт типобезопасность и улучшает DX
- Отличная поддержка PWA через vite-plugin-pwa
- shadcn/ui предоставляет качественные компоненты с возможностью кастомизации

**Альтернативы рассмотренные:**
- Next.js — избыточен для PWA без SSR
- Vue.js — меньше готовых решений для PWA
- Svelte — меньше сообщество, сложнее найти решения

### Backend: Python + FastAPI

**Решение:** Использовать FastAPI как основной фреймворк.

**Обоснование:**
- Асинхронный из коробки — важно для парсинга и уведомлений
- Автоматическая генерация OpenAPI документации
- Встроенная валидация через Pydantic
- Высокая производительность
- Простота написания и поддержки кода

**Альтернативы рассмотренные:**
- Django — избыточен, Django REST Framework тяжеловесен
- Flask — нет async из коробки, больше бойлерплейта

### База данных: PostgreSQL

**Решение:** PostgreSQL как основная СУБД.

**Обоснование:**
- Надёжность и производительность
- Поддержка JSON для гибких структур данных
- Хорошая интеграция с SQLAlchemy
- Бесплатная и open-source

---

## 2. Архитектурные решения

### Структура API

**Решение:** RESTful API с версионированием.

```
/api/v1/auth/*
/api/v1/schedule/*
/api/v1/subjects/*
/api/v1/works/*
...
```

**Обоснование:**
- Простота и понятность
- Версионирование позволяет безболезненно обновлять API
- Стандартные HTTP методы (GET, POST, PUT, DELETE)

### Аутентификация: JWT

**Решение:** JWT токены с access (15 мин) и refresh (7 дней).

**Обоснование:**
- Stateless — не требует хранения сессий на сервере
- Хорошо подходит для PWA
- Простая реализация с PyJWT (решение #21: миграция с python-jose)

### Парный режим

**Решение:** Оба пользователя имеют доступ ко всем данным, но:
- Общие данные (subjects, works, teachers) — редактируют оба
- Персональные данные (WorkStatus, Attendance) — только владелец

**Обоснование:**
- Минимизация дублирования данных
- Возможность видеть прогресс партнёра
- Чёткое разделение ответственности

### Парсинг расписания

**Решение:** httpx для парсинга HTTP API, APScheduler для фоновых задач.

**Обоснование:**
- ОмГУ предоставляет JSON API (`eservice.omsu.ru/schedule/backend/schedule/group/{group_id}`)
- httpx — async HTTP-клиент, нативно работает с FastAPI event loop
- SHA-256 хеширование ответа для определения изменений (без лишних записей в БД)
- APScheduler встраивается в FastAPI lifespan — не нужен отдельный процесс (решение #20)

---

## 3. Структура базы данных

### Ключевые таблицы

```
users               — пользователи (макс 2)
semesters            — семестры
subjects             — предметы (привязка к семестру)
schedule_entries     — записи расписания
schedule_snapshots   — снапшоты для отслеживания изменений
works                — учебные работы
work_statuses        — статусы работ (per user)
work_status_history  — история изменений статусов
teachers             — преподаватели
absences             — пропуски занятий (per user)
departments          — подразделения универа
buildings            — корпуса
classmates           — одногруппники
files                — файлы
lesson_notes         — заметки к предметам (per user)
lk_credentials       — зашифрованные данные ЛК (per user)
session_grades       — оценки из ЛК
semester_disciplines — дисциплины учебного плана из ЛК
telegram_links       — привязка Telegram аккаунтов (per user)
calendar_feeds       — токены iCalendar подписок (per user)
widget_api_keys      — API-ключи для виджетов (per user)
```

### Связи
- `subjects` → `semesters` (many-to-one)
- `works` → `subjects` (many-to-one)
- `work_statuses` → `works`, `users` (many-to-one)
- `schedule_entries` → `subjects`, `teachers` (many-to-one, nullable)
- `absences` → `users`, `schedule_entries` (many-to-one)
- `files` → `subjects`, `users` (many-to-one)

---

## 4. Принципы разработки

### Код
- Type hints обязательны (Python, TypeScript)
- Docstrings в формате Google (Python)
- Компоненты — функциональные (React)
- Атомарные коммиты с conventional commits

### Тестирование
- Unit-тесты для бизнес-логики
- Integration-тесты для API
- Минимальное покрытие: 80%

### Безопасность
- Никаких секретов в коде
- Валидация всех входных данных (Pydantic)
- HTTPS в продакшене
- Защита от CSRF, XSS

---

## 5. PWA требования

- Service Worker для offline-режима
- Web App Manifest
- Уведомления через Telegram бот (решение #26)
- Установка на домашний экран
- Кеширование статики и API-ответов

---

---

## 6. Windows-специфичные решения

### PostgreSQL: локальная установка вместо Docker

**Решение:** На Windows использовать локально установленный PostgreSQL вместо Docker.

**Обоснование:**
- asyncpg (асинхронный драйвер PostgreSQL для Python) имеет критические проблемы на Windows при подключении к PostgreSQL в Docker:
  - `ConnectionResetError` из-за `ProactorEventLoop` (дефолтный event loop на Windows)
  - Проблемы с кодировкой сообщений об ошибках (cp1251 vs UTF-8)
- Альтернативные драйверы (psycopg, psycopg_async, aiopg) либо не поддерживаются в SQLAlchemy 2.0 async, либо имеют те же проблемы с кодировкой
- Локальный PostgreSQL работает стабильно с asyncpg

**Альтернативы рассмотренные:**
- `WindowsSelectorEventLoopPolicy` — не помогло
- Драйвер `psycopg` вместо `asyncpg` — проблемы с кодировкой и аутентификацией
- Драйвер `aiopg` — не поддерживается в SQLAlchemy 2.0 async mode
- WSL2 — избыточно для данного проекта

### Vite: явное указание host

**Решение:** В `vite.config.ts` явно указывать `host: '127.0.0.1'`.

**Обоснование:**
- На Windows `localhost` может резолвиться в IPv6 (`::1`), а Vite по умолчанию слушает только IPv4
- Явное указание `127.0.0.1` гарантирует работу на всех Windows-машинах

---

## 7. Frontend решения

### Tailwind CSS v4

**Решение:** Использовать Tailwind CSS v4 с новым синтаксисом `@theme`.

**Обоснование:**
- Tailwind v4 использует новый подход к конфигурации через CSS `@theme` директиву
- Старый синтаксис с `@layer base` и CSS-переменными не работает
- `@apply` для кастомных классов типа `border-border` не поддерживается — нужно использовать прямые CSS-свойства

### Регистрация: двухэтапный процесс

**Решение:** После успешной регистрации автоматически выполнять логин.

**Обоснование:**
- Backend `/auth/register` возвращает `UserResponse`, а не токены
- Для получения JWT токенов необходимо вызвать `/auth/login`
- Улучшает UX — пользователю не нужно вводить данные повторно

---

## 8. Календарь и время

### react-day-picker v9 вместо нативного date input

**Решение:** Использовать react-day-picker v9 с Popover вместо нативного `<input type="date">`.

**Обоснование:**
- Нативный date input вызывает `onChange` при навигации по месяцам в некоторых браузерах
- Это приводит к нежелательному обновлению страницы при простом просмотре календаря
- react-day-picker даёт полный контроль над поведением — дата меняется только при клике на конкретный день

**Реализация:**
- `@radix-ui/react-popover` для выпадающего окна
- `react-day-picker` v9 для календаря
- `date-fns` для локализации (русский язык)

### Локальное время вместо UTC

**Решение:** Все функции работы с датами используют локальное время браузера.

**Обоснование:**
- `new Date().toISOString()` возвращает UTC, что вызывает проблемы около полуночи
- Например, в 0:45 по Омску (UTC+6) `toISOString()` вернёт предыдущий день (18:45 UTC)
- Функции `getToday()`, `addDays()`, `isToday()` переписаны на локальное время

---

## 9. Загрузка файлов

### Аватарки: локальное хранение

**Решение:** Хранить аватарки локально в папке `uploads/avatars/`.

**Обоснование:**
- Простая реализация без внешних сервисов
- FastAPI StaticFiles для отдачи файлов
- Уникальные имена через UUID
- Валидация типа и размера файла (max 5MB, только изображения)

**Реализация:**
- `POST /api/v1/uploads/avatar` — загрузка
- `DELETE /api/v1/uploads/avatar/{filename}` — удаление
- Защита от path traversal атак

### photo_url: str вместо HttpUrl

**Решение:** Использовать `str` вместо `HttpUrl` для поля `photo_url` в схемах Classmate.

**Обоснование:**
- При загрузке аватарок сохраняется относительный путь (`/uploads/avatars/...`)
- `HttpUrl` требует полный URL с протоколом, что не подходит для относительных путей
- `str` позволяет хранить как полные URL, так и относительные пути

---

---

## 10. Code Review решения (2026-02-06)

### httpOnly cookies и JWT revocation — отложены

**Решение:** Не включать переход с localStorage на httpOnly cookies и механизм отзыва JWT в текущий PR.

**Обоснование:**
- Это масштабная переделка всей auth-системы (backend endpoints + frontend store + 264 теста)
- Лучше делать отдельным PR с фокусированным ревью
- Текущая JWT-реализация достаточна для MVP с 2 пользователями

### Rate limiting: slowapi

**Решение:** Использовать slowapi для rate limiting на auth endpoints.

**Обоснование:**
- Простая интеграция с FastAPI
- 5/minute на login, 3/minute на register — достаточно для защиты от brute-force
- Не требует внешних зависимостей (Redis) для простых случаев

### Upload security: magic bytes вместо расширений

**Решение:** Валидировать загружаемые файлы по magic bytes (сигнатуре), а не по расширению.

**Обоснование:**
- Расширение файла легко подделать
- Magic bytes (JPEG: FF D8 FF, PNG: 89 50 4E 47, WEBP: RIFF...WEBP) надёжно идентифицируют формат
- Streaming чтение по чанкам 8KB защищает от DoS через огромные файлы

### Frontend: shared Modal с accessibility

**Решение:** Единый Modal компонент вместо локальных модалок на каждой странице.

**Обоснование:**
- DRY: код модалки повторялся на 5 страницах
- Accessibility: role="dialog", aria-modal, ESC handler, focus management — реализованы один раз
- Единообразный UX

### Frontend: sonner вместо alert()

**Решение:** Использовать библиотеку sonner для toast-уведомлений вместо browser alert().

**Обоснование:**
- alert() блокирует UI и выглядит устаревшим
- sonner даёт неблокирующие toast-уведомления с автоскрытием
- Единый паттерн для success/error уведомлений во всём приложении

---

## 11. Frontend тестирование (2026-02-07)

### Vitest + @testing-library/react + MSW

**Решение:** Vitest как тестовый фреймворк, @testing-library/react для рендеринга, MSW для мокирования API.

**Обоснование:**
- Vitest нативно интегрируется с Vite (общая конфигурация, алиасы, плагины)
- @testing-library/react поощряет тестирование поведения, а не деталей реализации
- MSW перехватывает запросы на сетевом уровне — не нужно мокать axios напрямую
- jsdom как environment для имитации браузерного API

**Альтернативы рассмотренные:**
- Jest — требует отдельную конфигурацию трансформаций, дублирует то, что Vite уже делает
- Playwright/Cypress — E2E тесты избыточны для unit/integration уровня на этом этапе

### pool: 'forks' для Vitest на Windows

**Решение:** Использовать `pool: 'forks'` вместо дефолтного `pool: 'threads'`.

**Обоснование:**
- MSW + jsdom на Windows удерживают сокеты после завершения тестов
- `pool: 'forks'` использует child processes, которые гарантированно убиваются при завершении
- Все 70 тестов проходят корректно

---

## 12. PWA решения (2026-02-07)

### generateSW вместо injectManifest

**Решение:** Использовать `generateSW` (Workbox) для генерации Service Worker.

**Обоснование:**
- Стандартные стратегии кеширования покрывают все текущие потребности
- Не нужен кастомный SW-код
- Автоматический precaching app shell (JS/CSS/HTML)

**Альтернативы рассмотренные:**
- `injectManifest` — избыточен, нет потребности в кастомной SW-логике

### registerType: 'prompt'

**Решение:** Пользователь решает когда применять обновление SW.

**Обоснование:**
- `autoUpdate` может прервать работу пользователя посреди заполнения формы
- `prompt` показывает баннер "Доступна новая версия" с кнопкой "Обновить"
- Пользователь контролирует момент обновления

### NetworkFirst для API, precache для shell

**Решение:**
- App Shell (JS/CSS/HTML) — precache (Cache First)
- API `/api/v1/*` — NetworkFirst с таймаутом 3с и fallback на кеш (24h, 100 записей)

**Обоснование:**
- App shell меняется редко → precache оптимален
- API данные должны быть свежими → NetworkFirst с коротким таймаутом
- 24h TTL и 100 записей — разумный баланс между объёмом кеша и полезностью
- `method: 'GET'` — кешируем только GET-запросы, мутации не кешируем

### offline.html fallback

**Решение:** Статическая страница `public/offline.html` для навигационных запросов без кеша.

**Обоснование:**
- Если пользователь офлайн и precache не содержит нужный маршрут — вместо ошибки показываем понятную страницу
- `navigateFallback: 'index.html'` покрывает SPA-роутинг, `offline.html` — крайний fallback

### pwa-mock.ts для тестов

**Решение:** Вынести мок `virtual:pwa-register/react` в отдельный файл `src/test/pwa-mock.ts`.

**Обоснование:**
- `vi.hoisted()` нельзя экспортировать из `setup.ts` — ошибка `SyntaxError: Cannot export hoisted variable`
- Отдельный модуль позволяет импортировать мок-стейт и в `setup.ts`, и в тестовых файлах
- Сброс моков в `afterEach` в setup.ts — централизованный cleanup

---

## 13. Clickable schedule решения (2026-02-08)

### key prop вместо useEffect для сброса состояния модала

**Решение:** Разделить `LessonDetailModal` на обёртку и `LessonDetailContent`, используя `key={entry.id}` для сброса состояния.

**Обоснование:**
- React 19 ESLint запрещает `setState` внутри `useEffect` (`react-hooks/set-state-in-effect`)
- React 19 ESLint запрещает доступ к ref.current во время рендера (`react-hooks/refs`)
- `key` prop вызывает полное пересоздание компонента при смене entry — чистый сброс всего состояния
- `useState(entry.notes ?? '')` в `LessonDetailContent` — инициализация без side effects

### tsconfig.app.json exclude для тестов

**Решение:** Добавить exclude `__tests__`, `*.test.ts`, `*.test.tsx`, `test/` в tsconfig.app.json.

**Обоснование:**
- `tsc -b` (используется в `npm run build`) включал тестовые файлы, которые зависят от Vitest глобалов (describe, it, vi)
- tsconfig.app.json не имел exclude — тестовые файлы компилировались без типов Vitest
- Раньше скрывалось кэшем `.tsbuildinfo`, но при любом `--clean` build ломался

---

## 14. Progress bars решения (2026-02-08)

### Клиентский расчёт прогресса вместо backend endpoint

**Решение:** Расчёт прогресса выполняется на клиенте через `calculateSemesterProgress()`, а не через отдельный backend endpoint.

**Обоснование:**
- `GET /api/v1/works` уже возвращает все работы с `my_status` — всё необходимое для расчёта
- Нет необходимости создавать дополнительный endpoint ради агрегации
- Frontend группирует по `subject_id` и считает статусы — быстрая операция
- Данные уже кешируются через TanStack Query (`staleTime: 60000`)

### Статусы "completed": completed + submitted + graded

**Решение:** В расчёте прогресса три статуса считаются "выполненными": `completed`, `submitted`, `graded`.

**Обоснование:**
- Студент может считать работу завершённой на любом из этих этапов
- `completed` — выполнена, `submitted` — сдана преподавателю, `graded` — оценена
- `in_progress` считается отдельно (для отображения в badges)
- `not_started` и `null` (нет статуса) — одна категория "не начато"

### SubjectProgressCard с навигацией на WorksPage

**Решение:** Клик на карточку предмета навигирует на `/works?subject_id=X`.

**Обоснование:**
- Естественный UX: увидел прогресс → кликнул → увидел все работы по предмету
- WorksPage уже поддерживает фильтрацию по `subject_id` через query params
- Edit/Delete кнопки вынесены поверх карточки с `e.stopPropagation()`

---

## 15. File upload решения (2026-02-08)

### Модель File: immutable (без updated_at)

**Решение:** Модель `File` не содержит поле `updated_at` — файлы неизменяемы после загрузки.

**Обоснование:**
- Файлы не редактируются — только загружаются, скачиваются и удаляются
- Уменьшает количество полей и упрощает модель
- `created_at` достаточно для отслеживания времени загрузки

### stored_filename: UUID вместо оригинального имени

**Решение:** На диске файлы хранятся под UUID-именами (`{uuid}.{ext}`), оригинальное имя — в БД.

**Обоснование:**
- Исключает коллизии одинаковых имён файлов
- Предотвращает проблемы с спецсимволами в именах файлов
- Content-Disposition при скачивании возвращает оригинальное имя пользователю

### Нативный HTML5 Drag & Drop без библиотек

**Решение:** Использовать нативные события `dragover`/`dragleave`/`drop` вместо react-dropzone.

**Обоснование:**
- Одна зона загрузки — нет сложной логики (множественные файлы, вложенные зоны)
- Не добавляет лишнюю зависимость
- Полный контроль над визуальным feedback при перетаскивании

### FileCategory как StrEnum (backend) и as const (frontend)

**Решение:** Использовать `StrEnum` в Python и `as const` объект в TypeScript для категорий файлов.

**Обоснование:**
- `StrEnum` сериализуется в JSON как строка — удобно для API
- `as const` в TS даёт типобезопасность без overhead TypeScript enum
- Единый набор категорий: textbook, problem_set, lecture, lab, cheatsheet, other

---

## 16. Dark theme решения (2026-02-08)

### Custom hook вместо Zustand store

**Решение:** Использовать чистый модуль `lib/theme.ts` + `useTheme` hook вместо Zustand store.

**Обоснование:**
- Тема — простое UI-состояние (3 значения), не нужен глобальный store
- Чистый модуль тестируется без React
- Hook подписывается на `matchMedia` change events для режима `system`
- Нет лишних зависимостей

### Cycling button вместо dropdown

**Решение:** Одна кнопка с циклом light → dark → system (Sun → Moon → Monitor).

**Обоснование:**
- Меньше кликов: один клик вместо клик + выбор
- Компактнее: icon-only button занимает минимум места
- Иконки интуитивно понятны (Sun/Moon/Monitor — стандарт)

### FOUC prevention через inline script

**Решение:** Inline `<script>` перед `<style>` в `index.html`, читает localStorage и ставит `.dark` до первого рендера.

**Обоснование:**
- React рендерится после загрузки JS bundle — слишком поздно
- Inline script выполняется синхронно до первого paint
- Нет вспышки белого фона при загрузке в тёмной теме

### 500-level цвета без dark: вариантов

**Решение:** Не трогать цвета `*-500` (text-blue-500, bg-green-500 и т.д.).

**Обоснование:**
- 500-level цвета достаточно яркие и читаемы на обоих фонах
- Минимизация diff — меняем только то, что реально плохо читается
- `*-600` слишком тёмные для dark mode → добавлены `dark:*-400`

---

## 17. CI fix решения (2026-02-08)

### ESLint: globalIgnores для shadcn/ui

**Решение:** Добавить `src/components/ui` в `globalIgnores` в `eslint.config.js`.

**Обоснование:**
- shadcn/ui компоненты генерируются CLI, не наш код
- 3 ошибки (react-refresh/only-export-components, no-empty-object-type) не имеют смысла для сгенерированного кода
- Стандартная практика — исключать UI-библиотечные файлы из строгого линтинга

### uv sync --extra dev вместо --dev

**Решение:** В CI использовать `uv sync --extra dev` вместо `uv sync --dev`.

**Обоснование:**
- dev-зависимости (ruff, pytest) объявлены в `[project.optional-dependencies].dev`
- `uv sync --dev` устанавливает `[dependency-groups].dev`, которой в проекте нет
- `uv sync --extra dev` корректно устанавливает optional extras

### Кросс-платформенная path traversal защита

**Решение:** Явно отклонять `\` и `..` в filename до `Path.resolve()`.

**Обоснование:**
- На Linux `\` не является разделителем путей — `..\\..\\etc\\passwd` не распознаётся как path traversal через `resolve()`
- `resolve()` на Linux оставляет бэкслэш как часть имени файла → файл не найден → 404 вместо 400
- Явная проверка `'\\' in filename or '..' in filename` работает одинаково на всех ОС

---

## 18. Production Docker решения (2026-02-09)

### Multi-stage builds для backend и frontend

**Решение:** Использовать multi-stage Docker builds для обоих сервисов.

**Обоснование:**
- Backend: builder с uv (python:3.12-slim + `ghcr.io/astral-sh/uv:latest`) → runtime без uv и dev-зависимостей
- Frontend: node:22-alpine build → nginx:1.27-alpine serve (статика)
- Итоговые образы минимальны — нет build tools в runtime

### nginx как единая точка входа

**Решение:** nginx :80 → /api/ → backend, / → frontend static.

**Обоснование:**
- Единый порт для клиента, нет CORS-проблем
- Rate limiting на уровне nginx (30r/s API, 5r/m login/register) + backend slowapi
- `--proxy-headers` на uvicorn + `X-Forwarded-For` в nginx → slowapi получает реальный IP клиента
- Gzip, security headers, PWA caching (sw.js no-cache, assets/ immutable 1y) — на уровне nginx

### Memory limits ~1.4GB из 2GB

**Решение:** PostgreSQL 512MB, backend 512MB, Redis 192MB, nginx 128MB, certbot 64MB.

**Обоснование:**
- VPS с 2GB RAM — ~600MB остаётся для OS и буферов
- PostgreSQL tuning: shared_buffers=256MB, work_mem=4MB, max_connections=50
- Redis: maxmemory 128mb, allkeys-lru eviction, appendonly для persistence

### Non-root user в backend container

**Решение:** Создать пользователя `appuser` (UID 1000) и запускать uvicorn от него.

**Обоснование:**
- Минимизация attack surface — процесс не имеет root-привилегий
- Upload директории создаются с правами appuser

### sed для line endings в entrypoint.sh

**Решение:** `sed -i 's/\r$//'` на entrypoint.sh в Dockerfile.

**Обоснование:**
- Файл разрабатывается на Windows, где Git может сохранять CRLF
- Linux контейнер ожидает LF — CRLF ломает shebang (`/bin/sh\r: not found`)
- sed выполняется при build — гарантированно исправляет line endings

### CSP с unsafe-inline

**Решение:** `script-src 'self' 'unsafe-inline'` в Content-Security-Policy.

**Обоснование:**
- Inline script в index.html для FOUC prevention (тёмная тема) не может быть вынесен в файл — должен выполниться до загрузки CSS
- `unsafe-inline` — компромисс между безопасностью и UX

## 19. Production Deployment решения (2026-02-09)

### Регенерация секретов на сервере

**Решение:** Генерировать SECRET_KEY (64 символа) и POSTGRES_PASSWORD (32 символа) прямо на сервере через `openssl rand`.

**Обоснование:**
- Секреты не хранятся в git, не передаются через insecure каналы
- `openssl rand -hex 32` → 64 hex символа (достаточно для JWT)
- `openssl rand -base64 24` → ~32 base64 символа (достаточно для PostgreSQL)
- Защита от брутфорса и подделки токенов

### ALLOWED_ORIGINS в JSON формате

**Решение:** В `.env.production` хранить ALLOWED_ORIGINS как JSON-массив: `["http://89.110.93.63"]`.

**Обоснование:**
- Pydantic v2 для `list[str]` полей пытается парсить env-переменную как JSON
- Строковый формат (`http://89.110.93.63`) вызывает `JSONDecodeError`
- JSON-формат универсален для любого количества origins

### COPY README.md в backend Dockerfile

**Решение:** Копировать `README.md` перед `uv sync --frozen --no-dev` (установка самого проекта).

**Обоснование:**
- `pyproject.toml` содержит `readme = "README.md"`
- `uv sync` без `--no-install-project` устанавливает сам проект (hatchling требует README.md)
- Без файла: `OSError: Readme file does not exist: README.md`

### Приоритет исправлений при деплое

**Решение:** При обнаружении ошибки сборки/запуска — сначала фиксить локально, коммитить, пушить, затем пулить на сервере.

**Обоснование:**
- Git — единственный source of truth
- Локальные исправления на сервере ведут к divergence и конфликтам
- CI проверяет исправление перед деплоем

---

## 20. Schedule auto-sync решения (2026-02-10)

### APScheduler 3.x вместо Celery Beat

**Решение:** Использовать APScheduler `AsyncIOScheduler` в lifespan FastAPI вместо Celery Beat.

**Обоснование:**
- APScheduler встраивается в process FastAPI — не нужен отдельный процесс/контейнер
- Celery+Beat требует 2 дополнительных процесса (worker + beat) и настройку broker
- Для одной задачи каждые 6 часов Celery избыточен
- AsyncIOScheduler нативно работает с asyncio (FastAPI event loop)

**Альтернативы рассмотренные:**
- Celery Beat — требует worker + beat + broker, избыточно для 1 задачи
- Cron в Docker — требует supervisord или второй entrypoint, сложнее управлять
- asyncio.create_task + sleep — нет graceful shutdown, нет retry логики

### Redis distributed lock вместо file lock

**Решение:** Redis lock с `blocking=False` и TTL 600s для предотвращения одновременного запуска sync.

**Обоснование:**
- uvicorn с `--workers 2` запускает 2 процесса — каждый запустит свой scheduler
- File lock не работает между контейнерами (если масштабировать)
- Redis уже используется в стеке (redis:7-alpine для кеша)
- TTL 600s — auto-release если worker упал посреди sync
- `blocking=False` — не ждать lock, просто пропустить эту итерацию

### Initial sync в entrypoint.sh

**Решение:** Первичная синхронизация расписания при старте контейнера (если snapshot нет).

**Обоснование:**
- Первый деплой не будет ждать 6 часов до первого sync
- Non-blocking (`|| echo WARNING`) — если sync упадёт, контейнер всё равно стартует
- Проверяет `get_latest_snapshot(db)` — если данные есть, пропускает sync

---

## 21. Vitest Windows workaround (2026-02-11)

### Claude Code test-runner agent вместо fix Vitest

**Решение:** Создать Claude Code агент `.claude/agents/test-runner.md` для запуска тестов с автоматическим kill зависшего процесса.

**Обоснование:**
- Vitest 4.0.18 имеет memory leak (GitHub issue #9560) — OOM при cleanup на Windows
- jsdom/MSW удерживают сокеты — процесс не завершается после тестов
- `--forceExit` не существует в Vitest (в отличие от Jest)
- Downgrade до 4.0.4 убирает OOM, но процесс всё равно зависает
- Агент запускает `vitest run` в фоне, парсит stdout на строку ` Test Files `, затем убивает процесс через TaskStop
- Прагматичный workaround — тесты проходят корректно, проблема только в cleanup

**Альтернативы рассмотренные:**
- `poolOptions.forks.singleFork: true` — deprecated в Vitest 4
- `forks.execArgv: ['--max-old-space-size=8192']` — не помогло
- Downgrade Vitest — зависание остаётся
- Custom Node.js script с taskkill — слишком хрупко

### formatTimeUntil: минуты вместо секунд

**Решение:** `formatTimeUntil()` принимает минуты, не секунды.

**Обоснование:**
- Backend `GET /schedule/today` возвращает `time_until_next` в минутах (`int(diff.total_seconds() // 60)`)
- Функция изначально была написана для секунд, что давало некорректное отображение
- Дополнительно SchedulePage вручную делил `time_until_next / 60` — двойная ошибка, показывало часы вместо минут

---

## 22. Notes per-subject решения (2026-02-11)

### UNIQUE constraint по subject_name вместо schedule_entry_id

**Решение:** Изменить UNIQUE constraint с `(user_id, schedule_entry_id)` на `(user_id, subject_name)`.

**Обоснование:**
- Заметка к "Математический анализ" должна быть видна при клике на любую пару этого предмета, не только на конкретный entry
- Один пользователь = одна заметка на предмет (upsert-семантика)
- `schedule_entry_id` и `lesson_date` остаются как информационные поля (последнее место редактирования)

### Upsert вместо 409 Conflict

**Решение:** POST `/api/v1/notes/` работает как upsert: 201 (new) или 200 (updated).

**Обоснование:**
- 409 Conflict заставлял клиент делать GET → проверка → POST/PUT — лишние запросы
- Upsert атомарен: одна операция вместо трёх
- Фронтенд autosave не различает "создать" и "обновить" — upsert упрощает логику

### Query по subject_name вместо entry_id в LessonDetailModal

**Решение:** `useQuery(['note-for-subject', entry.subject_name])` вместо `['note-for-entry', entry.id]`.

**Обоснование:**
- Заметка привязана к предмету, не к конкретной паре
- `key={entry.subject_name}` на LessonDetailContent — React пересоздаёт компонент при смене предмета
- Cache invalidation: `queryClient.invalidateQueries(['note-for-subject', ...])` + `['notes']`

### .env симлинк на сервере

**Решение:** Создать `.env → .env.production` симлинк в `/opt/repos/studyhelper`.

**Обоснование:**
- Docker Compose автоматически читает `.env` (не `.env.production`)
- При `docker compose up -d` без `.env` переменные `POSTGRES_USER` и др. пусты
- `pg_isready -U ""` падает → db unhealthy → backend не стартует
- Симлинк решает проблему без дублирования файла

---

## 23. Code Review Final решения (2026-02-14)

### structlog ProcessorFormatter вместо замены логгеров

**Решение:** Использовать structlog `ProcessorFormatter` с `foreign_pre_chain` для перехвата stdlib `logging.getLogger()`.

**Обоснование:**
- 15+ модулей уже используют `logging.getLogger(__name__)` — менять их не нужно
- `ProcessorFormatter` перехватывает все stdlib log записи и обрабатывает их через structlog pipeline
- JSON output в production (`JSONRenderer`), colored console в dev (`ConsoleRenderer`)
- Единая точка конфигурации в `setup_logging(debug=bool)`

**Альтернативы рассмотренные:**
- Замена всех `logging.getLogger()` на `structlog.get_logger()` — 15+ файлов менять, больше diff
- loguru — ещё одна зависимость, менее стандартный подход

### ContextVar для request_id

**Решение:** `contextvars.ContextVar` для передачи request_id в structured logs.

**Обоснование:**
- ContextVar привязан к async контексту — каждый request видит свой ID
- structlog processor `add_request_id()` читает ContextVar и добавляет в event_dict
- Middleware ставит/сбрасывает ContextVar в dispatch/finally
- X-Request-ID из входящего запроса сохраняется или генерируется uuid4().hex[:12]

### Path normalization для Prometheus

**Решение:** Regex `/\d+(?=/|$)/` → `/{id}/` для нормализации path в метриках.

**Обоснование:**
- Без нормализации `/api/v1/subjects/1`, `/api/v1/subjects/2`, ... — отдельные timeseries
- Cardinality explosion → OOM в Prometheus при тысячах уникальных path
- Regex заменяет числовые сегменты: `/api/v1/subjects/5/works/123` → `/api/v1/subjects/{id}/works/{id}`
- `/metrics` и `/health` исключены из инструментации (бесполезный шум)

### /metrics без аутентификации, с nginx IP restriction

**Решение:** Endpoint `/metrics` без JWT auth, доступ ограничен через nginx allow/deny.

**Обоснование:**
- Prometheus scraper не умеет JWT — auth усложняет настройку
- nginx `allow 172.16.0.0/12; allow 10.0.0.0/8; deny all` — только Docker internal network
- Стандартный паттерн в production: сетевая изоляция вместо application-level auth для метрик

### respx вместо MagicMock для httpx тестов

**Решение:** Заменить `patch.object(parser._client, "get/post")` + MagicMock на `respx` transport-level mocking.

**Обоснование:**
- MagicMock подменяет методы на уже созданном AsyncClient — внутренний connection pool теряет state
- В CI (GitHub Actions) это вызывало deadlock (~5 минут зависания), 14 тестов пропускались
- respx работает на уровне httpx transport — client internals не затронуты
- `@respx.mock` decorator + `respx.get(url).mock(return_value=Response(...))` — чистый API
- Для тестов network error: `side_effect=httpx.RequestError()` (base class, NOT in RETRYABLE_EXCEPTIONS) — retry не срабатывает

---

## 24. PostgreSQL Backups решения (2026-02-15)

### Host-level cron вместо Docker backup контейнера

**Решение:** Использовать cron на хосте + `docker compose exec -T db pg_dump` вместо отдельного backup-контейнера.

**Обоснование:**
- Минимум инфраструктуры — не нужен ещё один контейнер (уже 5 шт.)
- cron на хосте надёжнее — работает даже если Docker-стек упал
- `docker compose exec -T` позволяет выполнить pg_dump в существующем контейнере db
- Простое обслуживание — обычный bash-скрипт, логи в `/var/log/`

### pg_dump --clean --if-exists

**Решение:** Добавить `--clean --if-exists` в pg_dump команду.

**Обоснование:**
- `--clean` добавляет DROP TABLE перед CREATE TABLE в дампе
- `--if-exists` предотвращает ошибки при восстановлении в пустую БД
- Без `--clean` restore поверх существующей БД даёт ошибки "table already exists"

### flock для предотвращения параллельных бэкапов

**Решение:** `flock -n 200` на `/var/lock/studyhelper-backup.lock` в начале backup.sh.

**Обоснование:**
- Если предыдущий бэкап не завершился, cron запустит второй экземпляр
- Параллельные pg_dump могут конкурировать за ресурсы БД
- flock с `-n` (non-blocking) сразу завершается, если lock занят

---

## 25. Sentry Integration решения (2026-02-15)

### sentry-sdk[fastapi] с условной инициализацией

**Решение:** `sentry-sdk[fastapi]` на backend, `@sentry/react` на frontend. Инициализация только при наличии DSN.

**Обоснование:**
- SDK автоматически инструментирует FastAPI (middleware, exception handlers) — не нужно менять код
- `send_default_pii=False` — не отправлять персональные данные
- `traces_sample_rate=0.1` — 10% запросов для performance monitoring (Free tier: 5K errors/month)
- Без DSN приложение работает как раньше — graceful degradation

### VITE_SENTRY_DSN как Docker build arg

**Решение:** Передавать `VITE_SENTRY_DSN` через `build.args` в docker-compose.prod.yml и `ARG`/`ENV` в nginx/Dockerfile.

**Обоснование:**
- Vite подставляет `import.meta.env.*` при build time, не runtime
- Backend DSN — env var в контейнере (runtime), frontend DSN — build arg (build time)
- Пустой DSN → Sentry не инициализируется, нет overhead

### Sentry.setUser для user context

**Решение:** `Sentry.setUser({ id, username })` после login/register/fetchUser, `Sentry.setUser(null)` при logout.

**Обоснование:**
- Ошибки в Sentry привязаны к конкретному пользователю → проще дебажить
- Только id и username — без email/PII

---

## 26. Telegram Bot Simplification решения (2026-02-15)

### Удаление /week, /grades, /attendance

**Решение:** Убрать 3 команды из бота, оставить 9.

**Обоснование:**
- `/week` — длинное сообщение, часто превышает 4096 символов Telegram, требует split-логику
- `/grades` и `/attendance` — данные лучше смотреть в web UI с таблицами и графиками
- Меньше команд = проще меню, пользователь быстрее находит нужное

### ReplyKeyboardMarkup для быстрого доступа

**Решение:** Постоянная клавиатура с двумя кнопками: «📚 Расписание на сегодня» и «⏭ Следующее занятие».

**Обоснование:**
- Две самые частые операции — не нужно набирать `/today` или `/next`
- ReplyKeyboardMarkup с `resize_keyboard=True` — компактная, не занимает весь экран
- Кнопки появляются при `/start` и после `/link` — сразу доступны новому пользователю
- Обработчики `F.text` делегируют в существующие `cmd_today`/`cmd_next` — DRY

**Альтернативы рассмотренные:**
- InlineKeyboardMarkup — привязан к конкретному сообщению, не постоянный
- Только команды — требуют набора текста, менее удобно на мобильных

---

## 27. iCalendar Feed решения (2026-02-15)

### icalendar 7.x вместо ics или vobject

**Решение:** Использовать `icalendar>=7.0.0` для генерации ICS.

**Обоснование:**
- Stable release (Feb 2026), активно поддерживается
- Использует `zoneinfo` (Python 3.9+) — не нужен pytz
- API совместим с 4.x-6.x, проверенный в production
- `cal.add_missing_timezones()` автоматически добавляет VTIMEZONE для Asia/Omsk
- `vDuration` для REFRESH-INTERVAL (RFC 7986)

**Альтернативы рассмотренные:**
- `ics` — менее зрелая, ограниченная поддержка VALARM
- `vobject` — устаревшая, нет async-совместимости
- Ручная генерация ICS — error-prone, edge cases с timezone

### Token-based URL auth для публичного feed

**Решение:** Аутентификация .ics feed по секретному токену в URL, без JWT.

**Обоснование:**
- Стандарт для calendar feeds (Google Calendar, Apple iCal, Outlook — все используют URL-токены)
- Calendar клиенты не умеют JWT — невозможно добавить Authorization header
- `secrets.token_urlsafe(48)` → ~64 символа, 384 бита энтропии
- Rate limit 30/min на public endpoint через slowapi
- Регенерация токена инвалидирует старый URL

### base_url в Settings вместо hardcoded domain

**Решение:** Добавить `base_url: str = "https://studyhelper1.ru"` в `config.py`.

**Обоснование:**
- Feed URL строится как `{base_url}/api/v1/calendar/feed/{token}.ics`
- Hardcoded домен ломается при смене хоста или в dev-окружении
- Настраивается через env var `BASE_URL`

### Throttle last_accessed_at (1 раз/час)

**Решение:** Обновлять `last_accessed_at` не чаще раза в час.

**Обоснование:**
- Calendar клиенты обращаются к feed каждые 6-12 часов
- Без throttle каждый запрос → write в БД (лишняя нагрузка)
- `timedelta(hours=1)` — достаточная гранулярность для отображения "последнее обращение"

### VALARM за 24ч и 1ч для дедлайнов

**Решение:** Два напоминания для каждого deadline: за 24 часа и за 1 час.

**Обоснование:**
- 24ч — время подготовиться к сдаче
- 1ч — финальное напоминание
- Schedule entries без VALARM — у них есть `dtstart` в расписании, напоминание не нужно
- `vDuration(timedelta(hours=-24))` — стандартный trigger для VALARM

---

## 28. Phone Widget решения (2026-02-15)

### Shared schedule filter util

**Решение:** Вынести `_filter_entries()` из `calendar_feed.py` → `utils/schedule_filters.py` как `filter_entries_by_user_prefs()`.

**Обоснование:**
- Widget и Calendar Feed используют одну и ту же логику фильтрации (subgroup + PE teacher)
- DRY: один модуль, два потребителя
- Легко тестировать изолированно

### Query param auth для widget endpoint

**Решение:** `GET /next-lesson?api_key=xxx` — токен в query parameter, без JWT.

**Обоснование:**
- Scriptable (iOS) и HTTP Shortcuts (Android) не умеют JWT
- Query param — простейший способ передать токен из виджета
- Rate limit 60/min защищает от abuse
- Тот же паттерн, что и Calendar Feed (URL-based token auth)

### 7-day lookahead одним запросом

**Решение:** `get_schedule_entries_by_date_range(db, today, today+7)` — один SQL-запрос на все 7 дней.

**Обоснование:**
- Один запрос вместо цикла по дням → меньше нагрузка на БД
- Entries отсортированы по (lesson_date, start_time) — итерируем до первого подходящего
- 7 дней — разумный lookahead: покрывает выходные и праздники

### Nginx healthcheck: 127.0.0.1 вместо localhost

**Решение:** В healthcheck nginx использовать `http://127.0.0.1/health` вместо `http://localhost/health`.

**Обоснование:**
- Alpine Linux резолвит `localhost` в IPv6 `::1`
- nginx слушает только на IPv4 `0.0.0.0:80`
- `wget http://localhost/health` → Connection refused (пытается IPv6)
- `wget http://127.0.0.1/health` → 200 OK

---

## 29. Android Widget App решения (2026-02-16)

### AGP 9.0.0 с built-in Kotlin

**Решение:** Использовать AGP 9.0.0 без отдельного `org.jetbrains.kotlin.android` плагина.

**Обоснование:**
- AGP 9.0 (Jan 2026) включает Kotlin compiler по умолчанию
- Не нужен `id("org.jetbrains.kotlin.android")` — меньше boilerplate
- Kotlin версия управляется AGP, не вручную
- Gradle 9.3.1 — минимум для AGP 9.0

### RemoteViews вместо Jetpack Glance

**Решение:** Использовать классический `AppWidgetProvider` + `RemoteViews` вместо Jetpack Glance 1.1.0.

**Обоснование:**
- Виджет содержит 5 текстовых полей — Compose UI избыточен
- Glance тянет Compose runtime (+5-8 MB к APK)
- RemoteViews — проверенный API, работает на всех Android 8.0+
- Итоговый APK ~3.8 MB (debug) vs ~10+ MB с Glance

### SharedPreferences вместо EncryptedSharedPreferences

**Решение:** Обычные SharedPreferences для хранения API ключа и кеша.

**Обоснование:**
- EncryptedSharedPreferences deprecated в alpha07 (Apr 2025)
- Замена — DataStore + Tink, избыточно для API ключа расписания
- API ключ — не пароль, пользователь сам копирует из браузера

### Debug APK без release signing

**Решение:** CI собирает debug APK, release signing — на будущее.

**Обоснование:**
- Personal use — не нужна подпись для Google Play
- Release signing требует keystore + GitHub Secrets setup
- Debug APK устанавливается через "неизвестные источники"
- Структура для release signing уже заложена в app/build.gradle.kts (env vars)

### HttpURLConnection + org.json (built-in)

**Решение:** Использовать встроенные HttpURLConnection и org.json вместо OkHttp + Gson.

**Обоснование:**
- Минимальный APK — без внешних HTTP/JSON зависимостей
- Один GET-запрос — OkHttp interceptors/connection pooling не нужны
- `org.json.JSONObject` достаточен для парсинга простого JSON ответа
- Только `core-ktx`, `appcompat`, `work-runtime-ktx` как зависимости

### GitHub Actions CI для Android

**Решение:** Отдельный workflow `.github/workflows/android.yml` по тегу `android/v*`.

**Обоснование:**
- Не блокирует основной CI (backend/frontend)
- Tag-based trigger — сборка только при явном релизе
- `softprops/action-gh-release@v2` публикует APK в GitHub Releases
- `permissions: contents: write` — необходимо для создания release

---

## 30. "ауд." location parsing решения (2026-02-17)

### Strip "ауд." до dash-split в _parse_audit_corps

**Решение:** Стрипать `"ауд."/"аудитория"` prefix в начале `_parse_audit_corps`, до `split("-", 1)`.

**Обоснование:**
- API OmSU возвращает `"ауд. 114) Спортивный зал, 6("` для физкультуры
- Без strip: dash-split на `"ауд. 4-101"` даёт building=`"ауд. 4"` (некорректно)
- С strip: `"ауд. 4-101"` → `"4-101"` → dash-split корректен
- Для нового формата без dash: `num_match` извлекает room из начала, `bld_match` — building после запятой

**Альтернативы рассмотренные:**
- `aud_match` regex после dash-split — не защищает от `"ауд. 4-101"` формата
- Strip "ауд." только в `_clean_building` — слишком поздно, building уже содержит "ауд. 4"

### Defense-in-depth: "ауд." strip в _clean_room и frontend

**Решение:** `_clean_room` и frontend `formatLocation` тоже стрипают "ауд." prefix.

**Обоснование:**
- Parser — первая линия защиты, location utils — вторая
- Если другой источник данных передаст room как `"ауд. 301"`, utils обработают корректно
- Минимальный overhead — один regex sub

---

## 31. Code Review Fix решения (2026-02-17)

### _METRICS_ALLOWED_NETWORKS как модульная константа

**Решение:** Вынести `import ipaddress` и allowed_networks из тела функции на уровень модуля.

**Обоснование:**
- `import ipaddress` и создание `ip_network()` при каждом запросе — лишний overhead
- Модульная константа создаётся один раз при импорте
- Добавлена `192.168.0.0/16` — полное покрытие RFC 1918 частных сетей
- Fallback `403` при отсутствии `client_ip` — defense-in-depth (раньше пропускал запрос)

### REDISCLI_AUTH вместо redis-cli -a

**Решение:** `REDISCLI_AUTH=$REDIS_PASSWORD redis-cli ping` вместо `redis-cli -a $REDIS_PASSWORD ping`.

**Обоснование:**
- `-a` выводит warning "Using a password on the command line interface is not safe" в stderr
- Warning засоряет Docker healthcheck логи
- `REDISCLI_AUTH` env var — официальный способ подавления (Redis docs)

### GPG --passphrase-fd 0 вместо --passphrase

**Решение:** `printf '%s' "$KEY" | gpg --passphrase-fd 0 ...` вместо `gpg --passphrase "$KEY" ...`.

**Обоснование:**
- `--passphrase` CLI arg виден в `ps aux` как аргумент процесса
- `--passphrase-fd 0` читает passphrase из stdin — не виден в process list
- GnuPG документация рекомендует `--passphrase-fd` для scripted use

---

## 32. Release Signing решения (2026-02-17)

### Keystore через base64 GitHub Secret

**Решение:** Хранить keystore как base64-encoded GitHub Secret (`KEYSTORE_BASE64`), декодировать в CI.

**Обоснование:**
- Keystore — бинарный файл, не может быть GitHub Secret напрямую
- `base64 -d` в CI → `release.keystore` в android/app/ → Gradle подхватывает через env var
- `rm -f` с `if: always()` — cleanup даже при fail
- RSA 2048 / validity 10000 дней — стандартный баланс безопасности и срока действия

### Conditional release/debug build (fork-friendly)

**Решение:** CI собирает release APK если секреты заданы, иначе debug.

**Обоснование:**
- Форки не имеют доступа к secrets → `assembleDebug` как fallback
- `HAVE_SIGNING_KEY` job-level env → `if:` conditions на шагах
- Динамический APK path через `$GITHUB_OUTPUT`
- Release body указывает тип сборки ("Release (signed)" / "Debug (unsigned)")

### Gradle-native signing вместо external action

**Решение:** Использовать `signingConfigs` в build.gradle.kts с env vars, без `r0adkll/sign-android-release`.

**Обоснование:**
- build.gradle.kts уже содержит `signingConfigs` с `System.getenv()` — дополнительный action не нужен
- Меньше зависимостей в CI pipeline
- Signing интегрирован в Gradle build — один шаг вместо build + sign

---

## 33. CD (Continuous Deployment) решения (2026-02-18)

### Deploy job в существующем ci.yml

**Решение:** Добавить `deploy` job в конец `.github/workflows/ci.yml`, а не создавать отдельный workflow файл.

**Обоснование:**
- Один файл — один pipeline, `needs: [backend, frontend]` гарантирует порядок
- Автоматически наследует `on: push: branches: [main]`
- `if: github.event_name == 'push'` исключает PR из деплоя

### printf вместо heredoc для SSH config

**Решение:** Использовать `printf` в фигурных скобках для записи `~/.ssh/config`.

**Обоснование:**
- heredoc в YAML `run:` требует обязательных отступов → ломает синтаксис bash
- `printf` работает корректно с любым уровнем вложенности в YAML

### Сборка образов на сервере

**Решение:** `ssh prod deploy.sh` → `git pull` → `docker compose build --pull` → `up -d`.

**Обоснование:**
- Нет настройки Registry (GHCR/Docker Hub)
- Подходит для VPS с нормальным CPU (1-2 core)
- Если сервер начнёт тормозить — переделать на GHCR (build в CI, pull на сервере)

### Rollback через сохранённый SHA

**Решение:** `deploy.sh` сохраняет `PREVIOUS_SHA` в `/tmp/deploy_state`, `rollback.sh` делает `git reset --hard` и пересобирает.

**Обоснование:**
- Rollback запускается только если `steps.deploy.outcome == 'success'` — код уже обновлён, но health check упал
- Если `git pull` или `build` упали → старые контейнеры живы, rollback не нужен

---

## История изменений

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-02-03 | Создан документ | Инициализация проекта |
| 2026-02-04 | PostgreSQL локально на Windows | asyncpg + Docker несовместимы на Windows |
| 2026-02-04 | Vite host: 127.0.0.1 | IPv6/IPv4 проблемы на Windows |
| 2026-02-04 | Tailwind v4 @theme синтаксис | Новая версия требует новый подход |
| 2026-02-04 | Автологин после регистрации | Backend не возвращает токены при регистрации |
| 2026-02-05 | react-day-picker вместо native date | Контроль над onChange при навигации |
| 2026-02-05 | Локальное время вместо UTC | Корректная работа около полуночи |
| 2026-02-05 | photo_url: str вместо HttpUrl | Поддержка относительных путей для аватарок |
| 2026-02-05 | Локальное хранение аватарок | Простота реализации без внешних сервисов |
| 2026-02-06 | httpOnly cookies отложены | Масштабная переделка, отдельный PR |
| 2026-02-06 | slowapi для rate limiting | Простая защита auth endpoints от brute-force |
| 2026-02-06 | Magic bytes для upload | Надёжнее расширений, защита от подделки |
| 2026-02-06 | Shared Modal + sonner toasts | DRY, accessibility, UX |
| 2026-02-07 | Vitest + testing-library + MSW | Нативная интеграция с Vite, тесты поведения |
| 2026-02-07 | pool: 'forks' в Vitest | MSW + jsdom подвисают на Windows с threads |
| 2026-02-07 | generateSW для PWA | Стандартные стратегии, не нужен кастомный SW |
| 2026-02-07 | registerType: prompt | Пользователь контролирует момент обновления |
| 2026-02-07 | NetworkFirst для API (3s timeout) | Свежие данные с fallback на кеш |
| 2026-02-07 | pwa-mock.ts для тестов | vi.hoisted() нельзя экспортировать из setup.ts |
| 2026-02-08 | key prop для сброса состояния модала | React 19 ESLint запрещает setState в useEffect |
| 2026-02-08 | tsconfig.app exclude тестов | tsc -b включал тесты без Vitest типов |
| 2026-02-08 | Клиентский расчёт прогресса | GET /works уже содержит все данные для агрегации |
| 2026-02-08 | completed+submitted+graded = done | Три этапа завершённости работы |
| 2026-02-08 | SubjectProgressCard → WorksPage | Естественная навигация: прогресс → детали |
| 2026-02-08 | File immutable (без updated_at) | Файлы не редактируются |
| 2026-02-08 | stored_filename = UUID | Исключает коллизии и спецсимволы |
| 2026-02-08 | Нативный DnD без react-dropzone | Одна зона, не нужна библиотека |
| 2026-02-08 | FileCategory: StrEnum + as const | Удобная сериализация в API |
| 2026-02-08 | LessonNote отдельно от ScheduleEntry.notes | entry.notes — системные/парсерные, LessonNote — пользовательские |
| 2026-02-08 | Autosave debounce 500ms вместо кнопки | UX: не нужно помнить сохранять, меньше потерь данных |
| 2026-02-08 | getNoteForEntry: 404 → null | useQuery получает null как успешный результат, NoteEditor рендерится пустым |
| 2026-02-08 | noteEntryIds Set через отдельный query | Не модифицируем schedule API, заметки — отдельный домен |
| 2026-02-08 | Custom hook вместо Zustand для темы | Простое UI-состояние, не нужен store |
| 2026-02-08 | Cycling button для темы | Меньше кликов, компактнее dropdown |
| 2026-02-08 | Inline script для FOUC prevention | React рендерится слишком поздно |
| 2026-02-08 | 500-level цвета без dark: | Читаемы на обоих фонах, минимизация diff |
| 2026-02-08 | globalIgnores для shadcn/ui | Сгенерированный код не должен линтоваться строго |
| 2026-02-08 | uv sync --extra dev в CI | dev deps в optional-dependencies, не dependency-groups |
| 2026-02-08 | Явная проверка \\ и .. в filename | resolve() не ловит бэкслэш на Linux |
| 2026-02-09 | openssl rand для секретов | Генерация на сервере, не в git |
| 2026-02-09 | ALLOWED_ORIGINS в JSON | Pydantic требует JSON для list[str] |
| 2026-02-09 | COPY README.md в Dockerfile | uv sync устанавливает проект, hatchling требует readme |
| 2026-02-09 | Fix-commit-push-pull workflow | Git как source of truth, не править на сервере |
| 2026-02-09 | Multi-stage Docker builds | Минимальные образы без build tools |
| 2026-02-09 | nginx единая точка входа | Rate limiting + proxy-headers + PWA caching |
| 2026-02-09 | Memory limits ~1.4GB | VPS 2GB: 512+512+192+128+64(certbot) + OS headroom |
| 2026-02-09 | Non-root user в контейнере | Минимизация attack surface |
| 2026-02-09 | sed для line endings | Windows CRLF → Linux LF при build |
| 2026-02-09 | CSP unsafe-inline | FOUC prevention script требует inline |
| 2026-02-10 | APScheduler вместо Celery Beat | Одна задача, встраивается в FastAPI, не нужен worker |
| 2026-02-10 | Redis distributed lock | 2 uvicorn workers, нужна координация |
| 2026-02-10 | Initial sync в entrypoint.sh | Первый деплой не ждёт 6 часов |
| 2026-02-10 | jitter=60 в IntervalTrigger | 2 workers не стучатся в lock одновременно |
| 2026-02-10 | misfire_grace_time=3600 | Пропущенный job выполнится в течение часа |
| 2026-02-10 | Redis ping healthcheck | Мёртвый клиент пересоздаётся автоматически |
| 2026-02-10 | .gitattributes *.sh eol=lf | entrypoint.sh с CRLF не запустится в Docker |
| 2026-02-11 | test-runner agent вместо fix Vitest | OOM + hang на Windows, агент парсит вывод и убивает процесс |
| 2026-02-11 | formatTimeUntil принимает минуты | Backend отдаёт time_until_next в минутах |
| 2026-02-11 | UNIQUE по subject_name вместо entry_id | Заметка видна для любой пары предмета |
| 2026-02-11 | Upsert вместо 409 Conflict | Атомарная операция, проще autosave |
| 2026-02-11 | Query по subject_name в модале | Заметка per-subject, не per-entry |
| 2026-02-11 | .env симлинк на сервере | Docker Compose читает только .env |
| 2026-02-11 | CASCADE → SET NULL для absences FK | Посещаемость сохраняется при ресинке расписания (subject_name+lesson_date для идентификации) |
| 2026-02-11 | Убран StaticFiles mount /uploads | Файлы только через auth endpoint GET /api/v1/files/{id}/download |
| 2026-02-11 | python-jose → PyJWT | python-jose deprecated (последний релиз 2021), PyJWT активно поддерживается |
| 2026-02-11 | psycopg вместо psycopg2 в Alembic | psycopg2 ушёл как транзитивная зависимость aiopg, psycopg v3 уже установлен |
| 2026-02-11 | Redis authentication в production | --requirepass + REDIS_PASSWORD env var |
| 2026-02-11 | Пагинация limit/offset на list endpoints | files и notes: limit=50 default, max 200 |
| 2026-02-11 | Certbot webroot mode в Docker | Bootstrap скрипт решает chicken-and-egg (self-signed → real cert), certbot контейнер renew каждые 12ч |
| 2026-02-11 | 3 nginx server-блока для SSL | HTTP (ACME + redirect), HTTPS www (redirect → apex), HTTPS main (приложение) — чистое разделение ответственности |
| 2026-02-11 | Security headers дублируются в nested locations | nginx add_header в дочернем блоке сбрасывает все родительские add_header — HSTS/CSP явно повторяются |
| 2026-02-11 | STAGING mode в init-letsencrypt.sh | STAGING=1 для тестов без расхода лимитов Let's Encrypt (5 дубликатов/неделю) |
| 2026-02-14 | structlog ProcessorFormatter | Перехват stdlib logging, 0 изменений в 15+ модулях |
| 2026-02-14 | ContextVar для request_id | Per-request tracking через middleware + structlog processor |
| 2026-02-14 | Path normalization `/\d+/` → `/{id}/` | Предотвращение cardinality explosion в Prometheus |
| 2026-02-14 | /metrics без auth + nginx IP restrict | Prometheus scraper не умеет JWT, сетевая изоляция |
| 2026-02-14 | respx вместо MagicMock для httpx | MagicMock ломал connection pool → deadlock в CI |
| 2026-02-15 | Текущий семестр из SessionGrade, не из max(disciplines) | SemesterDiscipline содержит весь учебный план (1-11), max=11 для 3 курса — неверно. session_number парсинг + cap by plan |
| 2026-02-15 | Даты семестров: осень Sep1-Dec30, весна Feb9-Jul7 | Приблизительные, пользователь может изменить вручную. Не перезаписываются при re-import |
| 2026-02-15 | Host-level cron вместо Docker backup | Минимум инфраструктуры, работает если Docker упал |
| 2026-02-15 | pg_dump --clean --if-exists | DROP перед CREATE для корректного restore |
| 2026-02-15 | flock в backup.sh | Предотвращение параллельных pg_dump |
| 2026-02-15 | sentry-sdk[fastapi] + @sentry/react | Error tracking с graceful degradation без DSN |
| 2026-02-15 | VITE_SENTRY_DSN как build arg | Vite подставляет env при build time |
| 2026-02-15 | Sentry.setUser для user context | Привязка ошибок к пользователю |
| 2026-02-15 | setUser только с id, без username | username = email → PII leak в Sentry dashboard |
| 2026-02-15 | CSP connect-src *.ingest.sentry.io | Без этого frontend SDK не может отправить события |
| 2026-02-15 | EventScrubber + custom denylist | send_default_pii=False не scrub-ит exception args/locals |
| 2026-02-15 | traces_sampler вместо flat rate | Drop /health + /metrics, 100% auth/schedule, 20% rest — экономия free tier |
| 2026-02-15 | reactRouterV7BrowserTracingIntegration | Параметризованные transaction names + Web Vitals для react-router v7 |
| 2026-02-15 | React 19 onUncaughtError/onCaughtError | Component stack traces для ошибок вне ErrorBoundary |
| 2026-02-15 | DSN в .env, не .env.production | Docker Compose читает `.env` по умолчанию; `.env.production` — только для документации |
| 2026-02-15 | Удалены /week /grades /attendance из бота | Дублируют web UI, перегружают меню |
| 2026-02-15 | ReplyKeyboardMarkup вместо только команд | Кнопки внизу чата — быстрый доступ без набора / |
| 2026-02-15 | Reply-кнопки делегируют в cmd_today/cmd_next | DRY — единая логика для команд и кнопок |
| 2026-02-15 | icalendar 7.x для ICS генерации | Зрелая библиотека, zoneinfo, auto VTIMEZONE |
| 2026-02-15 | Token-based URL auth для feed | Стандарт calendar feeds, клиенты не умеют JWT |
| 2026-02-15 | base_url в Settings | Конфигурируемый домен вместо hardcode |
| 2026-02-15 | Throttle last_accessed_at 1 раз/час | Снижение write-нагрузки на БД |
| 2026-02-15 | VALARM 24ч + 1ч для дедлайнов | Два напоминания: подготовка + финальное |
| 2026-02-15 | Shared schedule filter util | DRY: calendar_feed + widget используют одну фильтрацию |
| 2026-02-15 | Query param auth для widget | Scriptable/HTTP Shortcuts не умеют JWT |
| 2026-02-15 | 7-day lookahead одним запросом | Один SQL вместо цикла по дням |
| 2026-02-15 | 127.0.0.1 вместо localhost в healthcheck | Alpine резолвит localhost в IPv6, nginx слушает IPv4 |
| 2026-02-16 | /today endpoint вместо расширения /next-lesson | Отдельный endpoint для обратной совместимости; весь день + future = offline кеш |
| 2026-02-16 | Локальный minutes_until в виджете | Сервер не знает точное время рендера виджета; локальное вычисление актуальнее |
| 2026-02-16 | 24h TTL на кеш виджета | Баланс: offline работает сутки, но не показывает недельной давности данные |
| 2026-02-16 | Shared _authenticate_by_token helper | DRY: next_lesson_by_token + today_schedule_by_token используют одну auth-логику |
| 2026-02-16 | AGP 9.0.0 с built-in Kotlin | Не нужен отдельный kotlin-android плагин, меньше boilerplate |
| 2026-02-16 | RemoteViews вместо Jetpack Glance | Glance тянет Compose runtime (+5-8 MB), для 5 текстовых полей избыточно |
| 2026-02-16 | SharedPreferences вместо EncryptedSharedPreferences | ESP deprecated (alpha07, Apr 2025), API ключ — не пароль |
| 2026-02-16 | Debug APK через GitHub Releases | Release signing требует keystore setup, debug достаточно для personal use |
| 2026-02-16 | HttpURLConnection + org.json (built-in) | Минимальный APK (~3.8 MB), без OkHttp/Gson зависимостей |
| 2026-02-17 | Strip "ауд." до dash-split | "ауд. 4-101" не ломает dash-split, "ауд. 114... 6(" парсится корректно |
| 2026-02-17 | Defense-in-depth "ауд." в _clean_room/frontend | Вторая линия защиты для room из любого источника |
| 2026-02-17 | _METRICS_ALLOWED_NETWORKS константа | import + ip_network при каждом запросе → модульная константа |
| 2026-02-17 | REDISCLI_AUTH вместо -a | Подавление password warning в healthcheck логах |
| 2026-02-17 | GPG --passphrase-fd 0 | Passphrase не виден в ps aux |
| 2026-02-17 | Keystore через base64 Secret | Бинарный keystore не может быть Secret напрямую, base64 decode в CI |
| 2026-02-17 | Conditional release/debug build | Fork-friendly: assembleRelease если секреты есть, assembleDebug иначе |
| 2026-02-17 | Gradle-native signing | signingConfigs уже в build.gradle.kts, external action не нужен |
| 2026-02-18 | CD: deploy job в ci.yml, не отдельный файл | Один файл — один pipeline, порядок jobs гарантирует needs |
| 2026-02-18 | printf вместо heredoc в SSH setup | heredoc в YAML run: требует отступы, ломает синтаксис |
| 2026-02-18 | StrictHostKeyChecking accept-new | SSH_KNOWN_HOSTS нет в секретах; accept-new безопаснее no |
| 2026-02-18 | Сборка образов на сервере (git pull + docker build) | Проще настройки; если тормозит — переделать на GHCR |
| 2026-02-18 | Rollback только если deploy успешен | git pull упал → старые контейнеры живы, откатывать нечего |
| 2026-02-19 | Redis lock для Telegram notification jobs | APScheduler 3.x не координирует jobs между workers; Redis lock по паттерну schedule_sync |
| 2026-02-19 | Исключение lesson_date из schedule hash | lesson_date меняется еженедельно без реальных изменений расписания → ложные уведомления |
