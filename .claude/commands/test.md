---
description: Запустить тесты и показать отчёт
---

# Test

Запусти тесты и проанализируй результаты.

## Шаги

### Backend
1. **Запусти все тесты**:
   ```bash
   cd backend && uv run pytest -v --tb=short
   ```

2. **Если есть падающие тесты**:
   - Покажи какие тесты упали
   - Объясни причину падения
   - Предложи исправление

3. **Проверь покрытие** (если запрошено):
   ```bash
   cd backend && uv run pytest --cov=src --cov-report=term-missing
   ```

### Frontend
4. **Запусти frontend тесты** (если есть):
   ```bash
   cd frontend && npm run test -- --run 2>/dev/null || echo "No frontend tests configured"
   ```

### Отчёт
5. **Сформируй отчёт**:
   - Backend: Всего / Passed / Failed / Skipped
   - Frontend: Всего / Passed / Failed / Skipped
   - Покрытие (если доступно)
   - Рекомендации по улучшению
