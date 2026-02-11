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
- Простая реализация с python-jose

### Парный режим

**Решение:** Оба пользователя имеют доступ ко всем данным, но:
- Общие данные (subjects, works, teachers) — редактируют оба
- Персональные данные (WorkStatus, Attendance) — только владелец

**Обоснование:**
- Минимизация дублирования данных
- Возможность видеть прогресс партнёра
- Чёткое разделение ответственности

### Парсинг расписания

**Решение:** Playwright для парсинга, Celery для фоновых задач.

**Обоснование:**
- Сайт ОмГУ использует JavaScript для рендеринга
- Playwright умеет работать с SPA
- Celery позволяет запускать парсинг по расписанию (cron)
- Хеширование расписания для определения изменений

---

## 3. Структура базы данных

### Ключевые таблицы

```
users              — пользователи (макс 2)
semesters          — семестры
subjects           — предметы (привязка к семестру)
schedule_entries   — записи расписания
schedule_snapshots — снапшоты для отслеживания изменений
works              — учебные работы
work_statuses      — статусы работ (per user)
work_status_history — история изменений статусов
teachers           — преподаватели
attendance         — посещаемость (per user)
departments        — подразделения универа
buildings          — корпуса
classmates         — одногруппники
files              — файлы
push_subscriptions — подписки на push
notification_settings — настройки уведомлений
```

### Связи
- `subjects` → `semesters` (many-to-one)
- `works` → `subjects` (many-to-one)
- `work_statuses` → `works`, `users` (many-to-one)
- `schedule_entries` → `subjects`, `teachers` (many-to-one, nullable)
- `attendance` → `users`, `schedule_entries` (many-to-one)
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
- Push-уведомления (Web Push API)
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

### Memory limits ~1.3GB из 2GB

**Решение:** PostgreSQL 512MB, backend 512MB, Redis 192MB, nginx 128MB.

**Обоснование:**
- VPS с 2GB RAM — ~700MB остаётся для OS и буферов
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
| 2026-02-09 | Memory limits ~1.3GB | VPS 2GB: 512+512+192+128 + OS headroom |
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
