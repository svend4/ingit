# Wiki: E-Commerce Platform MVP

## 📚 Содержание

- [Архитектура](architecture.md)
- [API Документация](api-docs.md)
- [Развертывание](deployment.md)
- [Руководство разработчика](developer-guide.md)

## 🎯 О проекте

E-Commerce Platform MVP - минимально жизнеспособный продукт платформы электронной коммерции.

### Основные возможности

- Каталог товаров с поиском и фильтрацией
- Корзина покупок
- Оформление заказа
- Интеграция с платежными системами
- Личный кабинет пользователя
- Административная панель

### Технологический стек

**Backend:**
- Python 3.11
- FastAPI
- PostgreSQL 15
- Redis 7
- Celery (для фоновых задач)

**Frontend:**
- React 18
- TypeScript 5
- Ant Design 5
- Redux Toolkit
- Vite

**Infrastructure:**
- Docker & Docker Compose
- Nginx
- GitHub Actions (CI/CD)
- DigitalOcean (хостинг)

## 🚀 Быстрый старт

### Требования

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Запуск локально

```bash
# Клонировать репозиторий
git clone https://github.com/example/ecommerce-mvp.git
cd ecommerce-mvp

# Запустить через Docker Compose
docker-compose up -d

# Backend будет доступен на http://localhost:8000
# Frontend будет доступен на http://localhost:3000
```

### Переменные окружения

Скопируйте `.env.example` в `.env` и настройте:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

## 📖 Документация

### Для разработчиков

- [Руководство по разработке](developer-guide.md)
- [Соглашения о коде](coding-conventions.md)
- [Git workflow](git-workflow.md)

### API

- [API Reference](api-docs.md)
- [Authentication](api-auth.md)
- [Error Handling](api-errors.md)

### Deployment

- [Deployment Guide](deployment.md)
- [Мониторинг](monitoring.md)
- [Backup & Recovery](backup.md)

## 👥 Команда

- **Иван Петров** - Team Lead & Backend Developer
- **Мария Сидорова** - Frontend Developer
- **Алексей Иванов** - Backend Developer

## 📞 Контакты

- **Email**: dev@example.com
- **Slack**: #ecommerce-mvp
- **Jira**: [Project Board](https://example.atlassian.net)
