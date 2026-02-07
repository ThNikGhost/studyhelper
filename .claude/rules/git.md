---
description: Git workflow and conventional commits
---

# Git Rules

## Формат коммитов (Conventional Commits)

```
type(scope): short description

[optional body]

[optional footer]
```

### Типы коммитов
- `feat`: новая функциональность
- `fix`: исправление бага
- `docs`: изменения в документации
- `style`: форматирование (не влияет на код)
- `refactor`: рефакторинг без изменения функциональности
- `test`: добавление/изменение тестов
- `chore`: обновление зависимостей, конфигов, скриптов

### Примеры
```
feat(auth): add JWT token refresh endpoint
fix(api): handle null response from external service
docs(readme): update installation instructions
refactor(db): extract connection logic to separate module
test(users): add unit tests for user service
chore(deps): update fastapi to 0.109.0
```

## Ветки

### Naming convention
- `main` — стабильная версия, деплоится на прод
- `develop` — разработка (опционально)
- `feature/название` — новая функциональность
- `fix/название` — исправление бага
- `hotfix/название` — срочное исправление на проде

### Workflow
1. Создай ветку от `main`
2. Делай атомарные коммиты
3. Пуш и создай PR
4. После ревью — merge в `main`
5. Удали feature-ветку

## Перед коммитом
- [ ] Тесты проходят: `pytest`
- [ ] Линтер не ругается: `ruff check .`
- [ ] Нет отладочного кода (print, console.log)
- [ ] Нет закомментированного кода
- [ ] Нет секретов в коде

## .gitignore обязательно
```
.env
.env.*
*.pyc
__pycache__/
.venv/
venv/
.idea/
.vscode/
*.log
.DS_Store
```
