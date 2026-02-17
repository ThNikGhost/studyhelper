# Текущая задача

## Статус
**Все post-MVP фичи реализованы. Проект в режиме поддержки.**

## Последняя сессия: Android Chronometer + Unified Location — 2026-02-17

### Сделано
- **Android Chronometer**: заменён статический текст обратного отсчёта на system `Chronometer` — посекундные тики при ~0% расхода батареи; "Сейчас" когда пара уже идёт. Обновлены оба layout (large + medium)
- **Backend location normalization**: `_parse_audit_corps` теперь обрабатывает строки в скобках и "зал" варианты; `format_location` нормализует "Корпус"/"корп." префиксы
- **Timeline building**: `TimelineExam` schema получила поле `building`, передаётся из semester service
- **Frontend location**: `formatLocation` убирает "Корпус"/"корп." префиксы; Timeline компоненты используют `formatLocation` для экзаменов
- **Коммит + тэг**: `f5f7769` → `android/v1.3.0` → CI сборка APK

### Файлы изменены
- `android/app/src/main/java/.../WidgetUpdater.kt` — Chronometer logic
- `android/app/src/main/res/layout/widget_layout.xml` — Chronometer view (large)
- `android/app/src/main/res/layout/widget_layout_medium.xml` — Chronometer view (medium)
- `backend/src/parser/omsu_parser.py` — parenthesized audit parsing
- `backend/src/utils/location.py` — format_location normalization
- `backend/src/schemas/semester.py` — TimelineExam.building field
- `backend/src/services/semester.py` — pass building to timeline
- `frontend/src/lib/dateUtils.ts` — formatLocation cleanup
- `frontend/src/components/timeline/TimelineBar.tsx` — use formatLocation
- `frontend/src/components/timeline/TimelineEventList.tsx` — use formatLocation
- `frontend/src/types/timeline.ts` — building field
- `backend/tests/test_location.py` — new test file
- Tests updated: parser, LessonCard, LessonDetailModal, dateUtils

## Следующие шаги (по приоритету)
- Все post-MVP фичи реализованы
- (Будущее) Release signing: keystore + GitHub Secrets для signed APK

## Блокеры / Вопросы
- Нет
