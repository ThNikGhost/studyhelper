# Текущая задача

## Статус
**Проект в режиме поддержки. Все фичи реализованы и задеплоены.**

Последний коммит (2026-02-21): feat(classmates): split shared/per-user data into separate table.

### Что сделано в этой сессии (2026-02-21):
- feat(classmates): разделение данных одногруппников на общие и личные (per-user)
  - Новая таблица `classmate_details` (classmate_id + user_id, UNIQUE)
  - `classmates` хранит только: full_name, group_name, subgroup
  - Личные данные (short_name, email, phone, telegram, vk, photo_url, notes) — в details
  - Миграция: `j0k1l2m3n4o5_split_classmate_details.py`
  - Новый endpoint: `PUT /classmates/{id}/details` (upsert)
  - `GET /classmates` → list без details, `GET /classmates/{id}` → с details текущего user
  - Frontend: две секции формы, async openViewModal со спиннером, карточки с инициалами
  - 665 тестов (было 659), 26 тестов classmates (было 20) ✅

## Следующие шаги (по приоритету)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
