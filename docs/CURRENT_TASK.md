# Текущая задача

## Статус
**01-PWA завершена** — ветка `feature/pwa` готова к merge.

## Выполнено: 01-PWA (Progressive Web App)
- [x] `vite-plugin-pwa` установлен, `VitePWA()` в конфиге
- [x] Web manifest (name, icons, theme_color, display: standalone)
- [x] Мета-теги в index.html (theme-color, apple-mobile-web-app, description)
- [x] Placeholder иконки (pwa-192, pwa-512, apple-touch-icon, favicon.svg)
- [x] Workbox: precache app shell + NetworkFirst для `/api/v1/*`
- [x] `useNetworkStatus` хук (online/offline tracking)
- [x] `NetworkStatusBar` — amber баннер при офлайне
- [x] `UpdatePrompt` — баннер обновления SW (registerType: prompt)
- [x] `AppLayout` обёртка для всех protected routes
- [x] 5 страниц: кнопки disabled в офлайне
- [x] 17 новых тестов (всего 87 frontend тестов)
- [x] TypeScript, ESLint, vite build — всё чисто

## Следующие задачи (приоритет)
1. **04-dashboard-widget** — виджет "Ближайшее" на dashboard (P1)
2. **06-clickable-schedule** — кликабельные элементы расписания (P1)
3. **09-dark-theme** — тёмная тема (P2)
4. **07-progress-bars** — прогресс-бары по предметам (P2)
5. **03-file-upload-ui** — UI загрузки файлов (P1)
6. **05-ics-export** — экспорт в .ics (P2)
7. **02-push-notifications** — push-уведомления (P1, зависит от PWA ✅)
8. **08-attendance** — посещаемость (P2)
9. **10-lesson-notes** — заметки к парам (P2)
10. **11-semester-timeline** — timeline семестра (P3)

## Заметки
- Backend: 264 теста проходят
- Frontend: 87 тестов проходят
- Все линтеры чисты
- Деплой отложен (сервер не готов)

## Блокеры / Вопросы
Нет блокеров.
