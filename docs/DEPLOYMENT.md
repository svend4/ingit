# InGit Deployment Guide

Руководство по развертыванию InGit в различных окружениях.

---

## 📋 Оглавление

1. [Локальная разработка](#локальная-разработка)
2. [Docker развертывание](#docker-развертывание)
3. [Домашний NAS](#домашний-nas)
4. [Production сервер](#production-сервер)
5. [Облачные платформы](#облачные-платформы)
6. [Monitoring](#monitoring)

---

## 🖥️ Локальная разработка

### Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (или SQLite)
- Git 2.x
- Make (опционально)

### Быстрый старт

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-org/ingit.git
cd ingit

# 2. Установите зависимости
make dev-install

# 3. Настройте окружение
cp .env.example .env
# Отредактируйте .env

# 4. Запустите миграции
make migrate-up

# 5. Запустите dev серверы
make dev
```

**URLs:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Frontend: http://localhost:5173

---

## 🐳 Docker развертывание

### Development

```bash
# Запустить весь стек
docker-compose up -d

# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down
```

**Доступ:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Adminer: http://localhost:8080

### Production

```bash
# Собрать production образы
docker-compose build --build-arg BUILD_TARGET=production

# Запустить
docker-compose -f docker-compose.yml up -d

# Применить миграции
docker-compose exec backend alembic upgrade head
```

### С мониторингом

```bash
# Запустить с monitoring stack
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.monitoring.yml \
  up -d
```

**Мониторинг:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- Alertmanager: http://localhost:9093

---

## 🏠 Домашний NAS

### Synology NAS

#### Вариант 1: Docker через UI

1. Откройте **Docker** в DSM
2. Перейдите в **Registry** → Скачайте образы:
   - `postgres:15-alpine`
   - `redis:7-alpine`
3. Загрузите `docker-compose.yml` через **File Station**
4. В **Docker** → **Project** → Создайте новый проект
5. Выберите загруженный `docker-compose.yml`
6. Запустите проект

#### Вариант 2: SSH + docker-compose

```bash
# Подключитесь к NAS по SSH
ssh admin@nas.local

# Установите docker-compose (если нет)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Клонируйте проект
git clone https://github.com/your-org/ingit.git /volume1/docker/ingit
cd /volume1/docker/ingit

# Настройте .env
cp .env.example .env
vi .env  # Измените пароли

# Запустите
docker-compose up -d
```

#### Автозапуск

Создайте Scheduled Task в DSM:
- **Task**: `docker-compose -f /volume1/docker/ingit/docker-compose.yml up -d`
- **Schedule**: At boot-up

### QNAP NAS

```bash
# Подключитесь к QNAP
ssh admin@qnap.local

# Перейдите в Container Station
cd /share/Container/ingit

# Клонируйте и запустите
git clone https://github.com/your-org/ingit.git .
docker-compose up -d
```

### TrueNAS Scale

1. Откройте **Apps** → **Available Applications**
2. Если InGit есть в каталоге → Install
3. Или используйте **Launch Docker Image**:
   - Image: `ghcr.io/your-org/ingit-backend:latest`
   - Configure ports, volumes, env vars

---

## 🌐 Production сервер

### Ubuntu/Debian VPS

#### 1. Подготовка сервера

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установите docker-compose
sudo apt install docker-compose-plugin

# Создайте пользователя
sudo useradd -m -s /bin/bash ingit
sudo usermod -aG docker ingit
```

#### 2. Установка InGit

```bash
# Переключитесь на пользователя
sudo su - ingit

# Клонируйте репозиторий
git clone https://github.com/your-org/ingit.git
cd ingit

# Настройте окружение
cp .env.example .env

# ВАЖНО: Измените в .env
vi .env
# - SECRET_KEY (сгенерируйте: openssl rand -hex 32)
# - POSTGRES_PASSWORD
# - GRAFANA_PASSWORD
# - Настройте домен и CORS_ORIGINS
```

#### 3. SSL сертификат (Let's Encrypt)

```bash
# Установите certbot
sudo apt install certbot python3-certbot-nginx

# Получите сертификат
sudo certbot certonly --standalone -d ingit.yourdomain.com

# Сертификаты будут в /etc/letsencrypt/live/ingit.yourdomain.com/
```

#### 4. Nginx reverse proxy

```bash
sudo apt install nginx

# Создайте конфигурацию
sudo vi /etc/nginx/sites-available/ingit
```

```nginx
server {
    listen 80;
    server_name ingit.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ingit.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/ingit.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ingit.yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Активируйте конфигурацию
sudo ln -s /etc/nginx/sites-available/ingit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. Запуск InGit

```bash
# Запустите Docker Compose
docker-compose up -d

# Примените миграции
docker-compose exec backend alembic upgrade head

# Проверьте статус
docker-compose ps
docker-compose logs -f
```

#### 6. Systemd service (автозапуск)

```bash
sudo vi /etc/systemd/system/ingit.service
```

```ini
[Unit]
Description=InGit Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ingit/ingit
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=ingit

[Install]
WantedBy=multi-user.target
```

```bash
# Активируйте service
sudo systemctl enable ingit
sudo systemctl start ingit
```

---

## ☁️ Облачные платформы

### DigitalOcean

#### App Platform

1. Fork репозиторий на GitHub
2. Перейдите в **App Platform** → **Create App**
3. Подключите GitHub репозиторий
4. Configure:
   - **Backend**: Dockerfile build, port 8000
   - **Frontend**: Dockerfile build, port 80
   - **Database**: Managed PostgreSQL
   - **Redis**: Managed Redis
5. Add environment variables
6. Deploy

#### Droplet (ручная установка)

```bash
# Создайте Droplet (Ubuntu 22.04, 2GB RAM)
# Следуйте инструкциям из "Production сервер"
```

### AWS

#### ECS Fargate

1. Push Docker images в ECR
2. Создайте Task Definition
3. Создайте ECS Service
4. Configure ALB для routing
5. Используйте RDS для PostgreSQL
6. Используйте ElastiCache для Redis

#### Lightsail Containers

```bash
# Push image
docker tag ingit-backend:latest ingit-backend
aws lightsail push-container-image \
  --service-name ingit \
  --label backend \
  --image ingit-backend

# Create service через Lightsail Console
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/ingit-backend
gcloud builds submit --tag gcr.io/PROJECT_ID/ingit-frontend

# Deploy
gcloud run deploy ingit-backend \
  --image gcr.io/PROJECT_ID/ingit-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy ingit-frontend \
  --image gcr.io/PROJECT_ID/ingit-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📊 Monitoring

### Базовый мониторинг

```bash
# Запустите с monitoring stack
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.monitoring.yml \
  up -d
```

**Доступ:**
- Prometheus: http://your-server:9090
- Grafana: http://your-server:3001
- Alertmanager: http://your-server:9093

### Настройка Grafana

1. Откройте Grafana (admin/admin)
2. Добавьте Prometheus datasource:
   - URL: `http://prometheus:9090`
3. Импортируйте dashboards:
   - Node Exporter: ID 1860
   - PostgreSQL: ID 9628
   - Redis: ID 763

### Alerting

Настройте Alertmanager для отправки уведомлений:

```yaml
# monitoring/alertmanager.yml
route:
  receiver: 'email'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'

receivers:
  - name: 'email'
    email_configs:
      - to: 'admin@example.com'
        from: 'alerts@ingit.local'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_KEY'
```

---

## 🔒 Security Best Practices

### Обязательно

- ✅ Измените все пароли по умолчанию
- ✅ Используйте HTTPS (Let's Encrypt)
- ✅ Настройте firewall (ufw)
- ✅ Регулярно обновляйте Docker images
- ✅ Включите automatic backups

### Рекомендуется

- ✅ Используйте secrets management (Vault, AWS Secrets)
- ✅ Настройте VPN для доступа к admin панелям
- ✅ Включите 2FA для пользователей
- ✅ Настройте rate limiting
- ✅ Регулярный security audit

---

## 📦 Backup & Restore

### Backup базы данных

```bash
# PostgreSQL
docker-compose exec postgres pg_dump -U ingit ingit > backup-$(date +%Y%m%d).sql

# Или используйте автоматический скрипт
./scripts/backup.sh
```

### Backup файлов

```bash
# Создайте архив всех данных
tar -czf ingit-backup-$(date +%Y%m%d).tar.gz \
  storage/ \
  .env \
  docker-compose.yml
```

### Restore

```bash
# Восстановить БД
docker-compose exec -T postgres psql -U ingit ingit < backup-20260201.sql

# Восстановить файлы
tar -xzf ingit-backup-20260201.tar.gz
```

---

## 🔍 Troubleshooting

### Backend не запускается

```bash
# Проверьте логи
docker-compose logs backend

# Проверьте переменные окружения
docker-compose exec backend env

# Проверьте подключение к БД
docker-compose exec backend python -c "from ingit.db.base import engine; print(engine)"
```

### Database миграции failed

```bash
# Проверьте текущую версию
docker-compose exec backend alembic current

# Откатите на предыдущую
docker-compose exec backend alembic downgrade -1

# Повторите миграцию
docker-compose exec backend alembic upgrade head
```

### Out of memory

```bash
# Увеличьте лимиты в docker-compose.yml
services:
  backend:
    mem_limit: 1g
    memswap_limit: 1g
```

---

## 📞 Поддержка

- **Документация**: https://ingit.readthedocs.io
- **GitHub Issues**: https://github.com/your-org/ingit/issues
- **Community**: https://discord.gg/ingit

---

**Версия**: 1.0
**Дата**: 2026-02-01
**Автор**: InGit Development Team
