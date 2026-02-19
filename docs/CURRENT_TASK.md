# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован, протестирован и работает в проде.**

Последний коммит `db72b6d` (2026-02-19): fix(android) — fix FileProvider StringIndexOutOfBoundsException on APK install.

### Что сделано в этой сессии (2026-02-19):
- fix(android): исправлен краш при установке APK через FileProvider
  - `file_paths.xml`: `path="update.apk"` → `path="."` (FileProvider ожидает директорию, не файл)
  - Бамп версии: 1.3.0 → 1.3.2 (versionCode 8 → 9)
  - Тег `android/v1.3.2` → CI собрал и опубликовал release APK на GitHub Releases

## Следующие шаги (по приоритету)
- Деплой всех изменений на прод (миграции b2c3d4e5f6g8 + a1b2c3d4e5f7 + новые типы работ)
- Тестирование APK 1.3.2 на устройстве (обновление с 1.3.1 должно работать без краша)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
