# Demo Project: E-Commerce Platform MVP

Этот проект демонстрирует структуру и организацию InGit-репозитория.

## 📁 Структура проекта

```
demo-project/
├── 00_inbox/              # Временные файлы (не коммитятся)
├── 10_profile/            # Информация о проекте и команде
│   └── project.yaml       # Метаданные проекта
├── 20_timeline/           # Журнал событий по датам
│   └── 2026/
│       └── 2026-02.md     # События февраля 2026
├── 30_documents/          # Официальные документы
│   ├── contracts/         # Договоры
│   │   └── contract-001.yaml
│   └── specs/             # Технические спецификации
├── 40_finance/            # Финансовый учет
│   ├── expenses/          # Расходы
│   │   └── expense-2026-01-hosting.yaml
│   └── income/            # Доходы
│       └── income-2026-01-advance.yaml
├── 50_projects/           # Исходный код
│   └── backend/           # Backend проекта
├── 60_configs/            # Конфигурации
├── 70_tasks/              # Задачи
│   ├── backlog/           # Бэклог
│   │   └── task-002.yaml
│   ├── in-progress/       # В работе
│   │   └── task-001.yaml
│   └── done/              # Выполнено
│       └── task-000.yaml
├── 80_wiki/               # База знаний
│   └── README.md
└── 90_exports/            # Выгрузки из внешних систем
```

## 📝 Примеры YAML-метаданных

### Проект (10_profile/project.yaml)
Содержит информацию о проекте, команде, бюджете, технологиях.

### Задачи (70_tasks/)
Задачи организованы по статусам в подпапках:
- `backlog/` - запланированные задачи
- `in-progress/` - задачи в работе
- `done/` - завершенные задачи

Каждая задача - YAML-файл с метаданными.

### Документы (30_documents/)
Договоры, спецификации, отчеты с метаданными:
- Стороны договора
- Суммы и сроки
- Связанные файлы

### Финансы (40_finance/)
Учет доходов и расходов:
- Категоризация
- Связь с проектами и задачами
- Налогообложение
- Чеки и счета

### Timeline (20_timeline/)
Хронологический журнал событий проекта в markdown.

## 🚀 Как использовать

1. **Клонировать пример**:
   ```bash
   cp -r examples/demo-project my-project
   cd my-project
   git init
   ```

2. **Настроить Git hooks**:
   ```bash
   ../../scripts/install-hooks.sh
   ```

3. **Начать работу**:
   - Обновите `10_profile/project.yaml`
   - Создайте задачи в `70_tasks/backlog/`
   - Коммитьте изменения

4. **Автоматическая валидация**:
   При коммите pre-commit hook проверит:
   - YAML-синтаксис
   - Обязательные поля
   - Размер файлов
   - Отсутствие файлов из inbox

## 💡 Workflow

### Создание задачи
```bash
# Создайте YAML-файл
cat > 70_tasks/backlog/task-003.yaml <<EOF
type: task
title: "Название задачи"
status: backlog
priority: medium
assignee: your.name
estimated_hours: 8
EOF

# Закоммитьте
git add 70_tasks/backlog/task-003.yaml
git commit -m "Add task #3"
```

### Работа над задачей
```bash
# Переместите из backlog в in-progress
git mv 70_tasks/backlog/task-003.yaml 70_tasks/in-progress/

# Обновите статус в файле
sed -i 's/status: backlog/status: in_progress/' 70_tasks/in-progress/task-003.yaml

# Коммитьте с референсом на задачу
git commit -am "Start working on task #3"
```

### Закрытие задачи
```bash
# Коммит с ключевым словом "fixes" автоматически закроет задачу (через post-commit hook)
git commit -am "Implement feature, fixes #3"
```

## 📊 Генерация отчетов

См. `scripts/generate-report.py` для автоматической генерации отчетов на основе метаданных.

## 🔐 Шифрование

Папка `40_finance/` содержит критичные данные. Для шифрования:

```bash
# Зашифровать файл
age -e -r <public-key> -o expense.yaml.age expense.yaml

# Расшифровать
age -d -i <private-key> expense.yaml.age > expense.yaml
```

## 📚 Дополнительно

- См. [../../docs/METHODOLOGY.md](../../docs/METHODOLOGY.md) для полного описания
- См. [../../docs/IDEAS_AND_PROPOSALS.md](../../docs/IDEAS_AND_PROPOSALS.md) для best practices
