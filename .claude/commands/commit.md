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
   uv run pytest -q
   ```
   Если тесты падают — НЕ коммить, сначала исправь.

3. **Проверь линтинг:**
   ```bash
   uv run ruff check .
   ```
   Если есть ошибки — исправь перед коммитом.

4. **Добавь файлы:**
   ```bash
   git add -A
   ```

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

## Если что-то пошло не так
- Тесты падают → Исправь и попробуй снова
- Конфликт при пуше → `git pull --rebase` и разреши конфликты
- Забыл добавить файл → `git add file && git commit --amend`
