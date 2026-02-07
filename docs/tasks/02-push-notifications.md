# Задача: Push-уведомления о дедлайнах

## Приоритет: P1 (высокий)
## Сложность: Высокая
## Затрагивает: Backend + Frontend

## Описание
Уведомления о приближающихся дедлайнах: за 3 дня, за 1 день, в день сдачи. Утренняя сводка. Настройки для каждого пользователя.

## Зачем
Основная боль студентов — забыть про дедлайн. Push-уведомления решают эту проблему напрямую.

## Зависимости
- Требуется PWA (задача 01) — Service Worker нужен для получения push

---

## Чеклист

### Фаза 1: Backend — Web Push инфраструктура
- [ ] Добавить зависимость `pywebpush` в `pyproject.toml`
- [ ] Сгенерировать VAPID ключи (public + private), сохранить в `.env`
- [ ] Создать модель `PushSubscription` (user_id, endpoint, keys_p256dh, keys_auth, created_at)
- [ ] Создать модель `NotificationPreference` (user_id, deadline_3days, deadline_1day, deadline_today, morning_summary, morning_time, enabled)
- [ ] Alembic миграция для новых таблиц
- [ ] Создать `schemas/notification.py` (PushSubscriptionCreate, NotificationPreferenceResponse/Update)

### Фаза 2: Backend — API endpoints
- [ ] `POST /api/v1/notifications/subscribe` — сохранить push-подписку
- [ ] `DELETE /api/v1/notifications/unsubscribe` — удалить подписку
- [ ] `GET /api/v1/notifications/preferences` — получить настройки уведомлений
- [ ] `PUT /api/v1/notifications/preferences` — обновить настройки
- [ ] `GET /api/v1/notifications/vapid-key` — публичный VAPID ключ для фронтенда

### Фаза 3: Backend — Логика отправки
- [ ] Создать `services/notification.py`:
  - `send_push(subscription, title, body, data)` — отправка одного push
  - `check_deadlines()` — проверка дедлайнов и отправка уведомлений
  - `send_morning_summary(user_id)` — утренняя сводка
  - Обработка ошибок: удалять expired подписки (410 Gone)
- [ ] Интеграция с Celery Beat (или APScheduler для MVP):
  - Задача `check_deadlines`: каждый час
  - Задача `send_morning_summaries`: в настроенное время
- [ ] Таблица `SentNotification` для дедупликации (не отправлять повторно)

### Фаза 4: Frontend — Подписка на push
- [ ] Зарегистрировать push в Service Worker
- [ ] Запросить разрешение на уведомления (`Notification.requestPermission()`)
- [ ] При получении разрешения — отправить подписку на backend
- [ ] Обработать отказ — показать объяснение зачем нужны уведомления

### Фаза 5: Frontend — Настройки уведомлений
- [ ] Создать страницу/модалку `NotificationSettings`:
  - Переключатель: включить/выключить уведомления
  - Чекбоксы: за 3 дня, за 1 день, в день дедлайна
  - Утренняя сводка: вкл/выкл + выбор времени
- [ ] Добавить кнопку настроек в DashboardPage или в навигацию
- [ ] Создать `services/notificationService.ts`

### Фаза 6: Тесты
- [ ] Backend: тесты для notification service (отправка, дедупликация, preferences)
- [ ] Backend: тесты для API endpoints
- [ ] Frontend: тесты для NotificationSettings компонента

---

## Технические детали

### Модели БД
```python
class PushSubscription(Base):
    __tablename__ = 'push_subscriptions'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    endpoint: Mapped[str] = mapped_column(String(500), unique=True)
    keys_p256dh: Mapped[str] = mapped_column(String(200))
    keys_auth: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(default=func.now())

class NotificationPreference(Base):
    __tablename__ = 'notification_preferences'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    deadline_3days: Mapped[bool] = mapped_column(default=True)
    deadline_1day: Mapped[bool] = mapped_column(default=True)
    deadline_today: Mapped[bool] = mapped_column(default=True)
    morning_summary: Mapped[bool] = mapped_column(default=False)
    morning_time: Mapped[time] = mapped_column(default=time(8, 0))
```

### ENV переменные
```
VAPID_PRIVATE_KEY=...
VAPID_PUBLIC_KEY=...
VAPID_CLAIM_EMAIL=mailto:admin@studyhelper.ru
```

### Содержимое push-уведомлений
```
📚 Дедлайн через 3 дня
"Лабораторная работа №3 по Математическому анализу"
Срок сдачи: 15 февраля

📚 Дедлайн завтра!
"Курсовая работа по Программированию"
Срок сдачи: 10 февраля

🌅 Доброе утро! Сегодня:
• 3 пары (первая в 8:30)
• 1 дедлайн: Лабораторная по Физике
```

## Связанные файлы
- `backend/src/models/` — новые модели
- `backend/src/services/notification.py` — новый сервис
- `backend/src/routers/notifications.py` — новый роутер
- `frontend/src/services/notificationService.ts` — новый сервис
- `frontend/src/pages/` или `frontend/src/components/` — настройки
