# Текущая задача

## Статус
**Проект в режиме поддержки. CD реализован, протестирован и работает в проде.**

Последний коммит `8dec2ac` (2026-02-19): feat(works) — add diff_credit and colloquium work types.

### Что сделано в этой сессии (2026-02-19):
- feat(works): добавлены два новых типа работ — `diff_credit` (Дифф. зачёт) и `colloquium` (Коллоквиум)
  - Backend: WorkType enum в models/work.py и schemas/work.py
  - Frontend: WorkType константа + workTypeLabels в types/work.ts
  - Миграция не нужна (work_type хранится как String(20) в БД)
  - Тесты: 631 backend passed, 385 frontend passed

## Следующие шаги (по приоритету)
- Деплой всех изменений на прод (миграции b2c3d4e5f6g8 + a1b2c3d4e5f7 + новые типы работ)
- Сборка и тестирование Android APK с fix countdown (тег `android/v*` для release)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
