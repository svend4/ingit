# InGit Quick Start Guide

## 🚀 Быстрый старт за 5 минут

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/yourusername/ingit.git
cd ingit
```

### Шаг 2: Установка Git hooks

```bash
chmod +x scripts/install-hooks.sh
./scripts/install-hooks.sh
```

### Шаг 3 (Опционально): Запуск Backend

```bash
cd backend

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Создать БД
python -c "from ingit.db.models import create_tables; create_tables()"

# Запустить сервер
python -m ingit.main
```

Backend будет доступен на http://localhost:8000

**API Docs**: http://localhost:8000/api/docs

### Шаг 4 (Опционально): Запуск Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Запустить dev server
npm run dev
```

Frontend будет доступен на http://localhost:5173

### Шаг 5: Использование примеров

```bash
cd examples/demo-project

# Генерация отчета
python ../../scripts/generate-report.py . summary

# Посмотреть примеры YAML
cat 70_tasks/in-progress/task-001.yaml
```

## 📚 Что дальше?

### Изучите документацию
- [Методология](docs/METHODOLOGY.md) - философия и архитектура
- [Спецификация БД](docs/DATABASE_SPEC.md) - структура данных
- [API Reference](docs/API_SPEC.md) - описание endpoints
- [UI Wireframes](docs/UI_WIREFRAMES.md) - дизайн интерфейса

### Попробуйте примеры
```bash
# Создать свой проект на основе примера
cp -r examples/demo-project my-project
cd my-project

# Инициализировать Git
git init
git add .
git commit -m "Initial commit"

# Установить hooks
../../scripts/install-hooks.sh

# Теперь hooks будут валидировать YAML при коммите!
```

### Создайте первую задачу
```bash
cd my-project

cat > 70_tasks/backlog/task-001.yaml <<EOF
type: task
title: "Моя первая задача"
status: backlog
priority: medium
assignee: myusername
estimated_hours: 4
labels:
  - test
EOF

# Попробуйте закоммитить
git add 70_tasks/backlog/task-001.yaml
git commit -m "Add first task"

# Pre-commit hook провалидирует YAML!
```

## 🛠️ Команды разработки

### Backend
```bash
cd backend

# Тесты
pytest

# Линтеры
black .
flake8 .
mypy ingit/

# Запуск с автоперезагрузкой
uvicorn ingit.main:app --reload
```

### Frontend
```bash
cd frontend

# Тесты
npm test

# Линтеры
npm run lint
npm run format

# Build для продакшена
npm run build
```

## 📊 Генерация отчетов

```bash
# Краткая сводка
python scripts/generate-report.py examples/demo-project summary

# Детальный отчет по задачам
python scripts/generate-report.py examples/demo-project tasks

# Недельный отчет
python scripts/generate-report.py examples/demo-project weekly
```

## 🔧 Troubleshooting

### Pre-commit hook не работает
```bash
# Убедитесь что скрипт исполняемый
chmod +x scripts/hooks/pre-commit

# Переустановите hooks
./scripts/install-hooks.sh
```

### Backend не запускается
```bash
# Проверьте Python версию (нужна 3.11+)
python --version

# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

### Frontend не запускается
```bash
# Очистите кэш и переустановите
rm -rf node_modules package-lock.json
npm install
```

## 💡 Полезные ссылки

- [GitHub Issues](https://github.com/yourusername/ingit/issues)
- [Discussions](https://github.com/yourusername/ingit/discussions)
- [Contributing Guide](CONTRIBUTING.md)
- [Habr Article](https://habr.com/ru/articles/991080/) - вдохновение

## 🤝 Как помочь проекту

1. ⭐ Поставьте звезду на GitHub
2. 🐛 Сообщайте о багах
3. 💡 Предлагайте идеи
4. 📝 Улучшайте документацию
5. 💻 Вносите код

---

**Нужна помощь?** Создайте issue или напишите в Discussions!
