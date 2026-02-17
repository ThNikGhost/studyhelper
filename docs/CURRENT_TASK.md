# Текущая задача

## Статус
**Проект в режиме поддержки. Release signing реализован.**

## Последняя сессия: F6 Release Signing — 2026-02-17

### Сделано
- **`.github/workflows/android.yml`** — conditional release/debug build: decode keystore из base64 Secret, `assembleRelease` с env vars, fallback `assembleDebug` для форков, динамический APK path, cleanup keystore с `if: always()`
- **`android/app/.../UpdateChecker.kt`** — `APK_ASSET_NAME = "app-release.apk"`, удалён TODO
- **`android/app/build.gradle.kts`** — versionCode 8, versionName "1.3.0"
- **`docs/DECISIONS.md`** — раздел 32: Release Signing (keystore base64, conditional build, Gradle-native signing)

### Ручной шаг (вне кода)
1. Сгенерировать keystore: `keytool -genkeypair -v -keystore release.keystore -alias studyhelper -keyalg RSA -keysize 2048 -validity 10000`
2. Конвертировать: `base64 -w 0 release.keystore`
3. Добавить 4 GitHub Secrets: `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD`
4. Создать тег: `git tag android/v1.3.0 && git push origin android/v1.3.0`

### Нюанс: debug → release миграция
Android не позволяет обновить debug APK поверх release (разные сертификаты). Пользователям нужно удалить debug-версию и установить release заново.

## Следующие шаги (по приоритету)
- **CD (Continuous Deployment)** — автодеплой на прод при пуше в main (SSH + docker compose rebuild)
- (Фаза 3) httpOnly cookies — access in memory, refresh in httpOnly cookie
- (Фаза 3) JWT blacklist через Redis
- (Будущее) CSP: убрать `unsafe-inline` (hash-based или vite-csp-guard)

## Блокеры / Вопросы
- Нет
