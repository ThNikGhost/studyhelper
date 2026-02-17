# Текущая задача

## Статус
**Все post-MVP фичи реализованы. Проект в режиме поддержки.**

## Последняя сессия: Fix "ауд." location parsing — 2026-02-17

### Сделано
- **Parser fix**: `_parse_audit_corps` стрипает "ауд."/"аудитория" prefix до dash-split, затем `num_match` извлекает room из начала + building после запятой
- **Defense-in-depth**: `_clean_room` (backend) и `formatLocation` (frontend) стрипают "ауд." prefix перед обработкой
- **Code review**: выявлен edge case `"ауд. 4-101"` (dash + ауд. prefix), исправлен переносом strip до dash-split
- **Тесты**: +7 новых тест-кейсов (parser: 4, location: 3, frontend: 3)
- **Коммит**: `86336fb`

### Файлы изменены
- `backend/src/parser/omsu_parser.py` — `_parse_audit_corps()` refactored
- `backend/src/utils/location.py` — `_clean_room()` strips "ауд." prefix
- `frontend/src/lib/dateUtils.ts` — `formatLocation()` strips "ауд." prefix
- `backend/tests/test_parser.py` — 4 new test cases
- `backend/tests/test_location.py` — 3 new test cases + parametrize
- `frontend/src/lib/__tests__/dateUtils.test.ts` — 3 new test cases

## Следующие шаги (по приоритету)
- Все post-MVP фичи реализованы
- (Будущее) Release signing: keystore + GitHub Secrets для signed APK

## Блокеры / Вопросы
- Нет
