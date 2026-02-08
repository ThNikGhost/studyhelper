# План: 01-PWA (Progressive Web App)

## Scope
Превратить frontend в полноценное PWA: manifest, service worker, кеширование, offline UX, баннер обновлений.

## Ключевые решения

| Решение | Выбор | Почему |
|---------|-------|--------|
| SW генерация | `generateSW` (Workbox) | Стандартные стратегии кеширования, не нужен кастомный SW |
| Manifest | В `vite.config.ts` (плагин генерирует) | Один источник правды |
| Обновления SW | `registerType: 'prompt'` | Пользователь решает когда обновляться |
| Layout | Новый `AppLayout` для protected routes | DRY, место для индикаторов |
| Offline data | Только in-memory кеш TanStack Query | Persistent кеш — отдельная задача |
| Иконки | Placeholder PNG (синий квадрат "SH") | Заменим позже на дизайн |

## Фазы

### Фаза 1: Зависимости + Manifest + Иконки
- `npm install -D vite-plugin-pwa`
- Добавить `VitePWA()` в `vite.config.ts` (manifest, workbox, runtimeCaching)
- Обновить `index.html` — мета-теги: theme-color, apple-mobile-web-app-capable, description, apple-touch-icon
- Создать `src/vite-env.d.ts` — типы для `virtual:pwa-register/react`
- Создать placeholder иконки в `public/`: pwa-192x192.png, pwa-512x512.png, apple-touch-icon-180x180.png, favicon.ico

**Workbox стратегии:**
- App Shell (JS/CSS/HTML) — Cache First (precache)
- API `/api/v1/*` — Network First, fallback на кеш (24h, 100 записей)
- `navigateFallback: 'index.html'` для SPA routing offline

### Фаза 2: AppLayout + Network Status
- **Создать** `src/hooks/useNetworkStatus.ts` — хук отслеживания online/offline
- **Создать** `src/components/NetworkStatusBar.tsx` — amber баннер "Нет подключения" с иконкой WifiOff
- **Создать** `src/components/UpdatePrompt.tsx` — баннер "Доступна новая версия" + кнопка "Обновить"
- **Создать** `src/components/AppLayout.tsx` — обёртка: NetworkStatusBar + UpdatePrompt + children
- **Изменить** `src/App.tsx` — обернуть все ProtectedRoute в AppLayout

### Фаза 3: Offline Form Disabling
- **Изменить** 5 страниц — добавить `useNetworkStatus()`, disabled кнопки offline:
  - `WorksPage.tsx` — кнопки создания/редактирования/удаления
  - `SubjectsPage.tsx` — аналогично
  - `SemestersPage.tsx` — аналогично
  - `ClassmatesPage.tsx` — аналогично
  - `SchedulePage.tsx` — кнопка "Обновить с сайта ОмГУ"

### Фаза 4: Тесты
- **Изменить** `src/test/setup.ts` — мок `virtual:pwa-register/react`
- **Создать** тесты:
  - `src/hooks/__tests__/useNetworkStatus.test.ts` — online/offline/events/cleanup
  - `src/components/__tests__/NetworkStatusBar.test.tsx` — renders/hides по статусу
  - `src/components/__tests__/UpdatePrompt.test.tsx` — offlineReady/needRefresh/кнопки
  - `src/components/__tests__/AppLayout.test.tsx` — рендерит children + компоненты

## Файлы

| Файл | Действие |
|------|----------|
| `frontend/package.json` | Изменить (+ vite-plugin-pwa) |
| `frontend/vite.config.ts` | Изменить (+ VitePWA плагин) |
| `frontend/index.html` | Изменить (мета-теги) |
| `frontend/src/vite-env.d.ts` | Создать |
| `frontend/public/pwa-192x192.png` | Создать |
| `frontend/public/pwa-512x512.png` | Создать |
| `frontend/public/apple-touch-icon-180x180.png` | Создать |
| `frontend/public/favicon.ico` | Создать |
| `frontend/src/hooks/useNetworkStatus.ts` | Создать |
| `frontend/src/components/NetworkStatusBar.tsx` | Создать |
| `frontend/src/components/UpdatePrompt.tsx` | Создать |
| `frontend/src/components/AppLayout.tsx` | Создать |
| `frontend/src/App.tsx` | Изменить |
| `frontend/src/pages/WorksPage.tsx` | Изменить |
| `frontend/src/pages/SubjectsPage.tsx` | Изменить |
| `frontend/src/pages/SemestersPage.tsx` | Изменить |
| `frontend/src/pages/ClassmatesPage.tsx` | Изменить |
| `frontend/src/pages/SchedulePage.tsx` | Изменить |
| `frontend/src/test/setup.ts` | Изменить |
| `frontend/src/hooks/__tests__/useNetworkStatus.test.ts` | Создать |
| `frontend/src/components/__tests__/NetworkStatusBar.test.tsx` | Создать |
| `frontend/src/components/__tests__/UpdatePrompt.test.tsx` | Создать |
| `frontend/src/components/__tests__/AppLayout.test.tsx` | Создать |

**Итого:** 12 новых файлов, 11 изменённых.

## Коммиты (ветка `feature/pwa`)
1. `feat(frontend): add vite-plugin-pwa and manifest configuration`
2. `feat(frontend): add AppLayout with network status and update prompt`
3. `feat(frontend): disable forms in offline mode`
4. `test(frontend): add PWA component and hook tests`

## Верификация
1. `npm run build` — в `dist/` есть `sw.js` + `manifest.webmanifest`
2. `npm run test` — все тесты (70 старых + ~15 новых) проходят
3. `npm run lint` — без ошибок
4. `npm run preview` — SW регистрируется, install prompt работает
5. DevTools → Network → Offline → баннер появляется, кнопки disabled
6. Lighthouse PWA audit → 90+
