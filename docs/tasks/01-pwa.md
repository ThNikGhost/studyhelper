# Задача: PWA (Progressive Web App)

## Приоритет: P0 (критично)
## Сложность: Средняя
## Затрагивает: Frontend

## Описание
Превратить приложение в полноценное PWA: возможность установки на телефон, оффлайн-доступ к кешированным данным, splash screen.

## Зачем
Студенты используют приложение с телефона. Без PWA — это просто сайт, который нужно каждый раз открывать через браузер и который не работает без интернета.

---

## Чеклист

### Фаза 1: Manifest + иконки
- [ ] Создать `public/manifest.json` (name, short_name, icons, theme_color, background_color, display: standalone, start_url, scope)
- [ ] Сгенерировать иконки (192x192, 512x512, maskable) — можно использовать простой SVG-логотип
- [ ] Добавить `<link rel="manifest">` в `index.html`
- [ ] Добавить мета-теги: `theme-color`, `apple-mobile-web-app-capable`, `apple-mobile-web-app-status-bar-style`
- [ ] Добавить apple-touch-icon для iOS

### Фаза 2: Service Worker
- [ ] Установить `vite-plugin-pwa` (интеграция Workbox с Vite)
- [ ] Настроить в `vite.config.ts`: `VitePWA({ registerType: 'autoUpdate', ... })`
- [ ] Стратегия кеширования:
  - **App Shell** (HTML, CSS, JS) — Cache First
  - **API данные** (расписание, работы) — Network First с fallback на кеш
  - **Статика** (иконки, шрифты) — Cache First
- [ ] Реализовать оффлайн-страницу (`offline.html`) с сообщением "Нет подключения к интернету"
- [ ] Показывать баннер "Доступно обновление" при новой версии SW

### Фаза 3: Оффлайн UX
- [ ] Индикатор статуса сети (online/offline) в header
- [ ] При оффлайне показывать кешированные данные с пометкой "Данные могут быть устаревшими"
- [ ] Отключить формы создания/редактирования в оффлайне (показать сообщение)

### Фаза 4: Тестирование
- [ ] Проверить Lighthouse PWA Score
- [ ] Протестировать установку на Android (Chrome)
- [ ] Протестировать установку на iOS (Safari — Add to Home Screen)
- [ ] Проверить оффлайн-режим
- [ ] Проверить обновление SW

---

## Технические детали

### Зависимости
```bash
npm install -D vite-plugin-pwa
```

### vite.config.ts
```typescript
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'StudyHelper — Помощник студента',
        short_name: 'StudyHelper',
        description: 'Расписание, дедлайны и предметы для студентов ОмГУ',
        theme_color: '#1e40af',
        background_color: '#ffffff',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\..*\/api\/v1\//,
            handler: 'NetworkFirst',
            options: { cacheName: 'api-cache', expiration: { maxEntries: 50, maxAgeSeconds: 86400 } },
          },
        ],
      },
    }),
  ],
})
```

### Структура файлов
```
frontend/
├── public/
│   ├── manifest.json
│   ├── pwa-192x192.png
│   ├── pwa-512x512.png
│   ├── apple-touch-icon.png
│   └── offline.html
└── src/
    └── components/
        ├── NetworkStatus.tsx      # Индикатор online/offline
        └── UpdatePrompt.tsx       # Баннер обновления SW
```

## Связанные файлы
- `frontend/vite.config.ts`
- `frontend/index.html`
- `frontend/src/App.tsx`
