# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован, протестирован и работает в проде.**

Последний коммит `a078a04` (2026-02-19): fix(hidden-subjects) — filter hidden subjects from alternate entry indicators.

### Что сделано в этой сессии (2026-02-19):
- fix(hidden-subjects): скрытые предметы больше не показываются как жёлтые индикаторы "!" другой подгруппы
  - `allEntries` в SchedulePage.tsx теперь фильтрует по `hiddenNames`
  - Одна строка `.filter()` + обновление deps массива useMemo
  - ESLint clean, 385 frontend tests passed (3 pre-existing SchedulePage failures)

## Следующие шаги (по приоритету)
- Деплой всех изменений на прод (миграции b2c3d4e5f6g8 + a1b2c3d4e5f7 + новые типы работ)
- Сборка и тестирование Android APK с fix countdown (тег `android/v*` для release)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
