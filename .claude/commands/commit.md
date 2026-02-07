---
description: Проверить тесты, линтер и сделать коммит с пушем
---

# Commit Feature

Сделай коммит и пуш завершённой работы.

## Аргументы
$ARGUMENTS — описание того, что было сделано (опционально)

## Действия

1. **Проверь статус:**
   ```bash
   git status
   ```

2. **Проверь, что тесты проходят:**
   ```bash
   cd backend && uv run pytest -q
   ```
   ```bash
   cd frontend && npm run test -- --run 2>/dev/null || true
   ```
   Если тесты падают — НЕ коммить, сначала исправь.

3. **Проверь линтинг:**
   ```bash
   cd backend && uv run ruff check .
   ```
   Если есть ошибки — исправь перед коммитом.

4. **Добавь файлы:**
   - Добавляй конкретные файлы: `git add file1 file2`
   - НИКОГДА не используй `git add -A` или `git add .`
   - Проверь, что не добавляешь .env, секреты, бинарные файлы

5. **Сделай коммит:**
   - Используй conventional commits: `type(scope): description`
   - Типы: feat, fix, docs, refactor, test, chore
   - Описание на английском, кратко

6. **Запуш на GitHub:**
   ```bash
   git push
   ```

7. **Обнови docs/PROJECT_STATUS.md:**
   - Отметь задачу как выполненную
   - Добавь запись о коммите

## Примеры коммитов
```
feat(auth): add JWT token authentication
fix(api): handle null response from database
refactor(users): extract validation logic
test(products): add integration tests
docs(readme): update installation instructions
```
