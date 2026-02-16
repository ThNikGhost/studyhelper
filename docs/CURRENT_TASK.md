# Текущая задача

## Статус
**F5.2 Android Widget App завершён. Все post-MVP фичи реализованы.**

## Последняя сессия: F5.2 Android Widget App — 2026-02-16

### Сделано
- **Android проект**: полный Gradle-проект в `android/` (~30 файлов)
- **AGP 9.0.0**: built-in Kotlin (без отдельного kotlin-android плагина), Gradle 9.3.1
- **Виджет 4×2**: AppWidgetProvider + RemoteViews, тёмная тема (#1a1a2e), 4 состояния (NoKey, NoData, NoLessons, Lesson)
- **Data layer**: ApiClient (HttpURLConnection), PrefsManager (SharedPreferences, 24h cache TTL), WidgetRepository (fetch → cache → findNextLesson)
- **ConfigActivity**: ввод API ключа, save → first update → schedule WorkManager → RESULT_OK
- **WorkManager**: PeriodicWorkRequest 30 мин, NetworkType.CONNECTED constraint
- **CI pipeline**: `.github/workflows/android.yml` — debug APK build по тегу `android/v*`, publish в GitHub Releases
- **APK**: ~3.8 MB debug, опубликован в GitHub Releases (android/v1.0.0)
- **kwgt-setup.html**: добавлена рекомендация нативного APK

### CI исправления (5 итераций)
1. YAML parse error с secrets в `if` → упрощён до debug build
2. gradlew Permission denied → `git update-index --chmod=+x`
3. Gradle 9.2 не существует → 9.3.1
4. GitHub Release 403 → `permissions: contents: write`
5. Успешная сборка и публикация

### Файлы созданы
- `android/` — полный Android-проект (~30 файлов: build scripts, Kotlin source, XML resources)
- `.github/workflows/android.yml` — CI workflow

### Файлы изменены
- `frontend/public/kwgt-setup.html` — добавлен блок с рекомендацией нативного APK

## Следующие шаги (по приоритету)
- Все post-MVP фичи реализованы
- (Будущее) Release signing: keystore + GitHub Secrets для signed APK

## Блокеры / Вопросы
- Нет
