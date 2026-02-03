# Deployment Guide — StudyHelper

## Требования к серверу

- **OS:** Ubuntu 22.04+ / Debian 12+
- **RAM:** 2+ GB
- **Storage:** 20+ GB SSD
- **Docker:** 24.0+
- **Docker Compose:** 2.20+

---

## Локальная разработка

### 1. Клонирование репозитория
```bash
git clone https://github.com/[username]/studyhelper.git
cd studyhelper
```

### 2. Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте .env
```

### 3. Запуск через Docker Compose
```bash
docker-compose up -d --build
```

### 4. Применение миграций
```bash
docker-compose exec backend uv run alembic upgrade head
```

### 5. Доступ к приложению
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Production Deployment

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose-plugin -y
```

### 2. Клонирование и настройка

```bash
git clone https://github.com/[username]/studyhelper.git
cd studyhelper

cp .env.example .env
nano .env  # Заполните production значения
```

### 3. Настройка .env для production

```env
# Database
DATABASE_URL=postgresql+asyncpg://studyhelper:SECURE_PASSWORD@db:5432/studyhelper
POSTGRES_USER=studyhelper
POSTGRES_PASSWORD=SECURE_PASSWORD
POSTGRES_DB=studyhelper

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-very-long-and-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com

# Push Notifications
VAPID_PUBLIC_KEY=your-vapid-public-key
VAPID_PRIVATE_KEY=your-vapid-private-key
VAPID_CLAIMS_EMAIL=admin@yourdomain.com
```

### 4. Запуск

```bash
docker-compose -f docker-compose.prod.yml up -d --build

# Применение миграций
docker-compose -f docker-compose.prod.yml exec backend uv run alembic upgrade head
```

### 5. Настройка Nginx (reverse proxy)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

---

## Docker Compose Files

### docker-compose.yml (development)
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    command: npm run dev -- --host

volumes:
  postgres_data:
```

### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    depends_on:
      - db
      - redis
    restart: always

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: celery -A src.celery worker -l info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis
    restart: always

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: celery -A src.celery beat -l info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
      - frontend
    restart: always

volumes:
  postgres_data:
```

---

## Мониторинг и обслуживание

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f celery
```

### Перезапуск сервисов
```bash
docker-compose restart backend
docker-compose -f docker-compose.prod.yml restart
```

### Бэкап базы данных
```bash
# Создание бэкапа
docker-compose exec db pg_dump -U studyhelper studyhelper > backup_$(date +%Y%m%d).sql

# Восстановление
docker-compose exec -T db psql -U studyhelper studyhelper < backup_20240101.sql
```

### Обновление приложения
```bash
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec backend uv run alembic upgrade head
```

---

## Troubleshooting

### База данных не запускается
```bash
# Проверка логов
docker-compose logs db

# Проверка volumes
docker volume ls
docker volume inspect studyhelper_postgres_data
```

### Backend не видит базу данных
```bash
# Проверка сети
docker network ls
docker-compose exec backend ping db
```

### Миграции не применяются
```bash
# Проверка текущей версии
docker-compose exec backend uv run alembic current

# Генерация новой миграции
docker-compose exec backend uv run alembic revision --autogenerate -m "fix"
```
