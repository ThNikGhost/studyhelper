# Текущая задача

## Задача
Инициализация проекта и настройка окружения

## Описание
Создание базовой структуры проекта StudyHelper: настройка frontend (React + Vite), backend (FastAPI), Docker-конфигурации и документации.

## Критерии готовности
- [x] Создана структура папок проекта
- [x] Заполнена документация (CLAUDE.md, Decisions.md, планы)
- [ ] Инициализирован frontend (Vite + React + TypeScript)
- [ ] Инициализирован backend (FastAPI + структура)
- [ ] Создан docker-compose.yml для локальной разработки
- [ ] Создан .env.example с переменными окружения
- [ ] Создана схема БД (docs/database_schema.md)
- [ ] Тесты настроены и проходят
- [ ] Линтеры настроены и проходят

## Прогресс
- [x] Создать структуру папок
- [x] Заполнить CLAUDE.md
- [x] Заполнить Current_task.md
- [x] Заполнить Decisions.md
- [x] Заполнить project_status.md
- [x] Создать plans/MVP_plan.md
- [x] Создать plans/full_plan.md
- [x] Создать plans/future_features.md
- [ ] Инициализировать frontend/
- [ ] Инициализировать backend/
- [ ] Создать docker-compose.yml
- [ ] Создать .env.example
- [ ] Создать docs/database_schema.md
- [ ] Создать docs/API.md (базовая структура)
- [ ] Создать docs/deployment.md

## Заметки по реализации
1. Frontend: использовать `npm create vite@latest . -- --template react-ts`
2. Backend: структура с разделением на routers, services, models, schemas
3. Docker: PostgreSQL, Redis, Backend, Frontend (dev режим)

## Блокеры / Вопросы
— Нет —

## Следующие шаги
1. Инициализировать frontend с Vite + React + TypeScript
2. Настроить Tailwind CSS и shadcn/ui
3. Инициализировать backend с FastAPI
4. Настроить Docker Compose
