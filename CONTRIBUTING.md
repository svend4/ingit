# Contributing to InGit

Спасибо за интерес к проекту InGit! Мы рады любому вкладу.

## 📋 Как начать

1. **Fork репозитория**
2. **Клонируйте свой fork**:
   ```bash
   git clone https://github.com/your-username/ingit.git
   cd ingit
   ```
3. **Создайте ветку для изменений**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Настройка окружения

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Frontend
```bash
cd frontend
npm install
```

### Git Hooks
```bash
./scripts/install-hooks.sh
```

## 📝 Процесс разработки

1. **Создайте Issue** перед началом работы (если его нет)
2. **Пишите чистый код** следуя style guide
3. **Добавляйте тесты** для новой функциональности
4. **Обновляйте документацию**
5. **Создайте Pull Request**

## 🎨 Code Style

### Python
- Follow PEP 8
- Use Black для форматирования
- Use type hints
- Maximum line length: 100

### TypeScript/React
- Follow Airbnb style guide
- Use Prettier для форматирования
- Use functional components with hooks
- Use TypeScript strict mode

## ✅ Checklist перед PR

- [ ] Код проходит все линтеры (black, flake8, eslint)
- [ ] Все тесты проходят
- [ ] Добавлены новые тесты
- [ ] Документация обновлена
- [ ] Commit messages осмысленные
- [ ] Нет конфликтов с main веткой

## 🧪 Тестирование

### Backend
```bash
cd backend
pytest --cov=ingit
```

### Frontend
```bash
cd frontend
npm test
```

## 📄 Commit Messages

Используйте conventional commits:

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: новая возможность
- `fix`: исправление бага
- `docs`: изменения в документации
- `style`: форматирование, отступы
- `refactor`: рефакторинг кода
- `test`: добавление тестов
- `chore`: обновление зависимостей

**Примеры:**
```
feat(api): add user authentication endpoint
fix(tasks): resolve task status transition bug
docs(readme): update installation instructions
```

## 🐛 Reporting Bugs

При создании Issue для бага включите:
- Описание проблемы
- Шаги для воспроизведения
- Ожидаемое поведение
- Актуальное поведение
- Версия InGit
- ОС и окружение

## 💡 Feature Requests

При создании Issue для новой возможности:
- Опишите use case
- Объясните, почему это важно
- Предложите возможную реализацию (опционально)

## 📞 Где задать вопросы

- **GitHub Discussions** - для общих вопросов
- **GitHub Issues** - для багов и feature requests
- **Pull Request Reviews** - для вопросов по коду

## 📜 Лицензия

Делая вклад в проект, вы соглашаетесь что ваш код будет распространяться под MIT License.

---

**Спасибо за вклад в InGit!** 🚀
