# InGit: Техническая спецификация базы данных

## 1. Обзор

### 1.1. Назначение базы данных

База данных InGit хранит **метаданные и структурированную информацию**, дополняющую Git-репозитории:
- Проекты и их настройки
- Задачи и связи между ними
- Пользователи, команды, права доступа
- Метаданные документов
- Финансовые записи
- Логи и аудит
- Индексы для быстрого поиска

**Важно**: Сами файлы хранятся в Git-репозиториях, БД содержит только метаинформацию.

### 1.2. Выбор СУБД

#### Основная: SQLite
**Преимущества:**
- Не требует отдельного сервера
- Один файл БД, легко бэкапить
- Идеально для standalone и NAS режимов
- Отличная производительность для малых/средних данных
- Транзакции ACID

**Использование:**
- Desktop standalone режим
- Домашний NAS (до 20 пользователей)
- Разработка и тестирование

#### Опциональная: PostgreSQL
**Преимущества:**
- Высокая производительность при больших данных
- Мощные возможности индексации и поиска
- Репликация и отказоустойчивость
- Расширенные типы данных (JSON, arrays)

**Использование:**
- Корпоративные развертывания (20+ пользователей)
- Высоконагруженные инсталляции
- Требования к репликации

### 1.3. Принципы проектирования

1. **Normalized design** — избегать дублирования данных
2. **Soft deletes** — не удалять физически, использовать флаг deleted_at
3. **Audit trails** — отслеживание created_at, updated_at
4. **UUIDs for IDs** — глобально уникальные идентификаторы для синхронизации
5. **JSON для гибких данных** — дополнительные атрибуты в поле metadata

---

## 2. Схема базы данных

### 2.1. Общая структура

```
Основные сущности:
├── Users (пользователи)
├── Teams (команды)
├── Projects (проекты)
├── Repositories (Git-репозитории)
├── Tasks (задачи)
├── Documents (документы)
├── Financial_Records (финансы)
├── Tags (метки)
└── Audit_Logs (логи)

Связи:
├── TeamMembers (пользователи ↔ команды)
├── ProjectMembers (пользователи ↔ проекты)
├── TaskAssignments (задачи ↔ исполнители)
├── TaskDependencies (зависимости задач)
├── DocumentTags (документы ↔ метки)
└── Commits (связь с Git)
```

### 2.2. Детальные схемы таблиц

#### 2.2.1. Users (Пользователи)

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))), -- UUID
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL, -- bcrypt hash
    full_name TEXT,
    avatar_url TEXT,

    -- 2FA
    totp_secret TEXT,
    totp_enabled BOOLEAN DEFAULT 0,

    -- Роль
    role TEXT NOT NULL DEFAULT 'developer', -- owner, admin, developer, viewer

    -- Статус
    status TEXT NOT NULL DEFAULT 'active', -- active, inactive, suspended

    -- Метаданные
    preferences TEXT, -- JSON: UI settings, language, etc.
    metadata TEXT, -- JSON: дополнительные поля

    -- Аудит
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME,
    deleted_at DATETIME,

    -- Индексы
    CHECK (role IN ('owner', 'admin', 'developer', 'viewer')),
    CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
```

#### 2.2.2. Teams (Команды)

```sql
CREATE TABLE teams (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    description TEXT,
    avatar_url TEXT,

    -- Владелец команды
    owner_id TEXT NOT NULL,

    -- Метаданные
    metadata TEXT, -- JSON

    -- Аудит
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME,

    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE INDEX idx_teams_owner ON teams(owner_id);
```

#### 2.2.3. TeamMembers (Участники команд)

```sql
CREATE TABLE team_members (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member', -- lead, member

    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    left_at DATETIME,

    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(team_id, user_id)
);

CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);
```

#### 2.2.4. Projects (Проекты)

```sql
CREATE TABLE projects (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE, -- URL-friendly: my-project
    description TEXT,

    -- Владелец
    owner_id TEXT NOT NULL,
    owner_type TEXT NOT NULL DEFAULT 'user', -- user или team

    -- Статус
    status TEXT NOT NULL DEFAULT 'active', -- active, archived, suspended

    -- Видимость
    visibility TEXT NOT NULL DEFAULT 'private', -- private, internal, public

    -- Даты
    start_date DATE,
    end_date DATE,

    -- Финансы
    budget DECIMAL(15, 2),
    currency TEXT DEFAULT 'USD',

    -- Конфигурация
    default_branch TEXT DEFAULT 'main',
    settings TEXT, -- JSON: hooks, integrations, etc.

    -- Метаданные
    metadata TEXT, -- JSON

    -- Аудит
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME,

    FOREIGN KEY (owner_id) REFERENCES users(id),
    CHECK (owner_type IN ('user', 'team')),
    CHECK (status IN ('active', 'archived', 'suspended')),
    CHECK (visibility IN ('private', 'internal', 'public'))
);

CREATE INDEX idx_projects_owner ON projects(owner_id, owner_type);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_slug ON projects(slug);
```

#### 2.2.5. Repositories (Git-репозитории)

```sql
CREATE TABLE repositories (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL,

    -- Пути
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE, -- Абсолютный путь к .git

    -- Git info
    default_branch TEXT DEFAULT 'main',
    remote_url TEXT, -- Для синхронизации

    -- Статистика
    size_bytes INTEGER DEFAULT 0,
    commit_count INTEGER DEFAULT 0,
    last_commit_sha TEXT,
    last_commit_at DATETIME,

    -- Метаданные
    metadata TEXT, -- JSON

    -- Аудит
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_repos_project ON repositories(project_id);
CREATE INDEX idx_repos_path ON repositories(path);
```

#### 2.2.6. Tasks (Задачи)

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL,

    -- Идентификация
    number INTEGER NOT NULL, -- Автоинкремент в рамках проекта: #1, #2, ...
    title TEXT NOT NULL,
    description TEXT,

    -- Тип и статус
    type TEXT NOT NULL DEFAULT 'task', -- task, bug, feature, epic
    status TEXT NOT NULL DEFAULT 'backlog', -- backlog, todo, in_progress, review, done, cancelled
    priority TEXT NOT NULL DEFAULT 'medium', -- low, medium, high, urgent

    -- Назначение
    assignee_id TEXT, -- Исполнитель
    reporter_id TEXT NOT NULL, -- Кто создал

    -- Временные рамки
    start_date DATE,
    due_date DATE,
    estimated_hours DECIMAL(6, 2),
    actual_hours DECIMAL(6, 2) DEFAULT 0,

    -- Иерархия
    parent_task_id TEXT, -- Для subtasks
    epic_id TEXT, -- Связь с epic

    -- Метаданные
    labels TEXT, -- JSON array: ["backend", "security"]
    metadata TEXT, -- JSON

    -- Аудит
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    deleted_at DATETIME,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (reporter_id) REFERENCES users(id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id),
    FOREIGN KEY (epic_id) REFERENCES tasks(id),

    UNIQUE(project_id, number),
    CHECK (type IN ('task', 'bug', 'feature', 'epic', 'subtask')),
    CHECK (status IN ('backlog', 'todo', 'in_progress', 'review', 'blocked', 'done', 'cancelled')),
    CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_tasks_epic ON tasks(epic_id);
```

#### 2.2.7. TaskDependencies (Зависимости задач)

```sql
CREATE TABLE task_dependencies (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    task_id TEXT NOT NULL, -- Зависимая задача
    depends_on_task_id TEXT NOT NULL, -- От какой зависит

    type TEXT NOT NULL DEFAULT 'blocks', -- blocks, relates_to

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE(task_id, depends_on_task_id),
    CHECK (type IN ('blocks', 'relates_to', 'duplicates'))
);

CREATE INDEX idx_task_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_task_deps_depends ON task_dependencies(depends_on_task_id);
```

#### 2.2.8. Documents (Документы)

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL,
    repository_id TEXT,

    -- Идентификация
    title TEXT NOT NULL,
    file_path TEXT NOT NULL, -- Относительный путь в репозитории

    -- Тип
    type TEXT NOT NULL DEFAULT 'general', -- contract, spec, report, general

    -- Метаданные из YAML
    yaml_metadata TEXT, -- Полный YAML как JSON

    -- Извлеченные поля для индексации
    document_date DATE,
    parties TEXT, -- JSON array
    amount DECIMAL(15, 2),
    currency TEXT,
    valid_from DATE,
    valid_until DATE,
    document_status TEXT, -- active, expired, cancelled

    -- Файлы
    attached_files TEXT, -- JSON array путей
    checksum TEXT, -- SHA256

    -- Метаданные
    tags TEXT, -- JSON array
    metadata TEXT, -- JSON

    -- Аудит
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE SET NULL
);

CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_type ON documents(type);
CREATE INDEX idx_documents_date ON documents(document_date);
CREATE INDEX idx_documents_path ON documents(file_path);
```

#### 2.2.9. FinancialRecords (Финансовые записи)

```sql
CREATE TABLE financial_records (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL,

    -- Тип
    type TEXT NOT NULL, -- income, expense, budget
    category TEXT NOT NULL, -- Категория (зарплата, хостинг, и т.д.)

    -- Сумма
    amount DECIMAL(15, 2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',

    -- Описание
    title TEXT NOT NULL,
    description TEXT,

    -- Дата
    transaction_date DATE NOT NULL,

    -- Связи
    task_id TEXT, -- Связь с задачей (опционально)
    document_id TEXT, -- Связь с документом (счет, договор)

    -- Платежная информация
    payment_method TEXT, -- bank_card, cash, bank_transfer
    receipt_path TEXT, -- Путь к скану чека/счета

    -- Метаданные
    metadata TEXT, -- JSON

    -- Аудит
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL,

    CHECK (type IN ('income', 'expense', 'budget', 'forecast'))
);

CREATE INDEX idx_finance_project ON financial_records(project_id);
CREATE INDEX idx_finance_type ON financial_records(type);
CREATE INDEX idx_finance_date ON financial_records(transaction_date);
CREATE INDEX idx_finance_category ON financial_records(category);
```

#### 2.2.10. Commits (Связь с Git-коммитами)

```sql
CREATE TABLE commits (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    repository_id TEXT NOT NULL,

    -- Git данные
    sha TEXT NOT NULL UNIQUE,
    message TEXT NOT NULL,
    author_name TEXT NOT NULL,
    author_email TEXT NOT NULL,
    author_id TEXT, -- Связь с пользователем InGit

    commit_date DATETIME NOT NULL,

    -- Статистика
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,

    -- Связи
    task_ids TEXT, -- JSON array ID задач, упомянутых в сообщении

    -- Метаданные
    metadata TEXT, -- JSON

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_commits_repo ON commits(repository_id);
CREATE INDEX idx_commits_sha ON commits(sha);
CREATE INDEX idx_commits_date ON commits(commit_date);
CREATE INDEX idx_commits_author ON commits(author_id);
```

#### 2.2.11. Tags (Метки)

```sql
CREATE TABLE tags (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL,

    name TEXT NOT NULL,
    color TEXT DEFAULT '#808080', -- Цвет в hex
    description TEXT,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, name)
);

CREATE INDEX idx_tags_project ON tags(project_id);
```

#### 2.2.12. TaskTags (Связь задач и меток)

```sql
CREATE TABLE task_tags (
    task_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

#### 2.2.13. AuditLogs (Логи аудита)

```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    -- Кто
    user_id TEXT,
    username TEXT NOT NULL, -- Дублируем на случай удаления пользователя

    -- Что
    action TEXT NOT NULL, -- create, update, delete, login, etc.
    entity_type TEXT NOT NULL, -- task, project, user, etc.
    entity_id TEXT NOT NULL,

    -- Изменения
    old_values TEXT, -- JSON snapshot до изменения
    new_values TEXT, -- JSON snapshot после

    -- Контекст
    ip_address TEXT,
    user_agent TEXT,

    -- Метаданные
    metadata TEXT, -- JSON

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

#### 2.2.14. Sessions (Сессии пользователей)

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL,

    token TEXT NOT NULL UNIQUE, -- JWT или session token

    -- Информация о клиенте
    ip_address TEXT,
    user_agent TEXT,
    device_type TEXT, -- desktop, mobile, web

    -- Время жизни
    expires_at DATETIME NOT NULL,
    last_activity_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at DATETIME,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
```

#### 2.2.15. SyncQueue (Очередь синхронизации)

```sql
CREATE TABLE sync_queue (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    -- Тип операции
    operation TEXT NOT NULL, -- push, pull, conflict
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,

    -- Статус
    status TEXT NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed

    -- Приоритет
    priority INTEGER DEFAULT 5,

    -- Попытки
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    last_error TEXT,

    -- Данные
    payload TEXT, -- JSON данных для синхронизации

    -- Время
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    completed_at DATETIME,

    CHECK (operation IN ('push', 'pull', 'conflict')),
    CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX idx_sync_status ON sync_queue(status);
CREATE INDEX idx_sync_priority ON sync_queue(priority DESC);
CREATE INDEX idx_sync_created ON sync_queue(created_at);
```

---

## 3. Расширенные возможности

### 3.1. Full-Text Search (SQLite FTS5)

```sql
-- Виртуальная таблица для полнотекстового поиска
CREATE VIRTUAL TABLE tasks_fts USING fts5(
    task_id UNINDEXED,
    title,
    description,
    content='tasks',
    content_rowid='rowid'
);

-- Триггеры для автоматической синхронизации
CREATE TRIGGER tasks_ai AFTER INSERT ON tasks BEGIN
    INSERT INTO tasks_fts(task_id, title, description)
    VALUES (new.id, new.title, new.description);
END;

CREATE TRIGGER tasks_ad AFTER DELETE ON tasks BEGIN
    DELETE FROM tasks_fts WHERE task_id = old.id;
END;

CREATE TRIGGER tasks_au AFTER UPDATE ON tasks BEGIN
    UPDATE tasks_fts SET title = new.title, description = new.description
    WHERE task_id = new.id;
END;
```

### 3.2. Представления (Views)

#### Активные задачи с исполнителями
```sql
CREATE VIEW active_tasks_view AS
SELECT
    t.id,
    t.number,
    t.title,
    t.status,
    t.priority,
    t.due_date,
    p.name as project_name,
    u.full_name as assignee_name,
    u.email as assignee_email
FROM tasks t
JOIN projects p ON t.project_id = p.id
LEFT JOIN users u ON t.assignee_id = u.id
WHERE t.status IN ('todo', 'in_progress', 'review')
  AND t.deleted_at IS NULL
  AND p.deleted_at IS NULL;
```

#### Финансовая сводка по проектам
```sql
CREATE VIEW project_finances_view AS
SELECT
    p.id as project_id,
    p.name as project_name,
    p.budget,
    p.currency,
    COALESCE(SUM(CASE WHEN fr.type = 'income' THEN fr.amount ELSE 0 END), 0) as total_income,
    COALESCE(SUM(CASE WHEN fr.type = 'expense' THEN fr.amount ELSE 0 END), 0) as total_expenses,
    p.budget - COALESCE(SUM(CASE WHEN fr.type = 'expense' THEN fr.amount ELSE 0 END), 0) as remaining_budget
FROM projects p
LEFT JOIN financial_records fr ON p.id = fr.project_id AND fr.deleted_at IS NULL
WHERE p.deleted_at IS NULL
GROUP BY p.id;
```

### 3.3. Stored Procedures (для PostgreSQL)

```sql
-- Функция для автоинкремента номера задачи в проекте
CREATE OR REPLACE FUNCTION get_next_task_number(p_project_id TEXT)
RETURNS INTEGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    SELECT COALESCE(MAX(number), 0) + 1
    INTO next_num
    FROM tasks
    WHERE project_id = p_project_id;

    RETURN next_num;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического присвоения номера
CREATE OR REPLACE FUNCTION assign_task_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.number IS NULL THEN
        NEW.number := get_next_task_number(NEW.project_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_assign_number
BEFORE INSERT ON tasks
FOR EACH ROW
EXECUTE FUNCTION assign_task_number();
```

---

## 4. Миграции и версионирование

### 4.1. Стратегия миграций

Используем инструмент миграций (например, Flyway, Liquibase или собственный):

```
migrations/
├── V001__initial_schema.sql
├── V002__add_tasks_table.sql
├── V003__add_financial_records.sql
├── V004__add_fts_search.sql
└── V005__add_sync_queue.sql
```

### 4.2. Пример миграции

```sql
-- V001__initial_schema.sql
BEGIN TRANSACTION;

-- Таблица версий схемы
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Базовые таблицы
CREATE TABLE users (...);
CREATE TABLE projects (...);
-- ...

INSERT INTO schema_migrations (version, description)
VALUES (1, 'Initial schema');

COMMIT;
```

---

## 5. Производительность и оптимизация

### 5.1. Индексы

**Основные правила:**
- Индексы на внешние ключи (FOREIGN KEY)
- Индексы на поля, используемые в WHERE/JOIN
- Composite индексы для частых запросов
- Избегать индексов на редко используемые поля

### 5.2. Партиционирование (PostgreSQL)

Для больших таблиц (например, audit_logs):

```sql
-- Партиционирование по месяцам
CREATE TABLE audit_logs_2026_02 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE audit_logs_2026_03 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
```

### 5.3. Vacuum и обслуживание (SQLite)

```sql
-- Периодическая очистка
VACUUM;

-- Анализ для оптимизатора запросов
ANALYZE;
```

---

## 6. Безопасность БД

### 6.1. Шифрование (SQLite)

Использование SQLCipher для шифрования всей БД:

```sql
-- При создании БД
PRAGMA key = 'your-secret-passphrase';
PRAGMA cipher_page_size = 4096;
```

### 6.2. Права доступа

- **Пользователь приложения**: READ/WRITE доступ
- **Бэкап-пользователь**: READ-ONLY доступ
- **Админ**: полный доступ

### 6.3. SQL Injection Prevention

- Использовать prepared statements
- Валидация входных данных
- Parameterized queries

---

## 7. Бэкап и восстановление

### 7.1. Стратегия бэкапа

**SQLite:**
```bash
# Полный бэкап
sqlite3 ingit.db ".backup ingit-backup-$(date +%Y%m%d).db"

# Dump в SQL
sqlite3 ingit.db .dump > ingit-backup.sql
```

**PostgreSQL:**
```bash
# Полный бэкап
pg_dump -U ingit_user ingit_db > ingit-backup-$(date +%Y%m%d).sql

# Compressed
pg_dump -U ingit_user -F c ingit_db > ingit-backup.dump
```

### 7.2. Автоматизация

```bash
#!/bin/bash
# backup.sh

DB_PATH="/var/lib/ingit/ingit.db"
BACKUP_DIR="/var/backups/ingit"
DATE=$(date +%Y%m%d_%H%M%S)

# Бэкап БД
sqlite3 "$DB_PATH" ".backup $BACKUP_DIR/db-$DATE.db"

# Сжатие
gzip "$BACKUP_DIR/db-$DATE.db"

# Удаление старых (старше 30 дней)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/db-$DATE.db.gz"
```

---

## 8. Масштабирование

### 8.1. Шардирование

При очень больших данных можно разделить по проектам:

```
ingit_shard_1.db  # Проекты 1-1000
ingit_shard_2.db  # Проекты 1001-2000
...
```

### 8.2. Репликация (PostgreSQL)

- **Master-Slave** для распределения нагрузки чтения
- **Multi-Master** для распределенных команд

### 8.3. Кэширование

- Redis для кэширования частых запросов
- In-memory кэш в приложении

---

## 9. Мониторинг

### 9.1. Метрики

- Размер БД
- Количество записей в таблицах
- Производительность запросов
- Рост данных (records/day)

### 9.2. Алерты

- Размер БД > 80% доступного места
- Медленные запросы (> 1 сек)
- Ошибки синхронизации

---

## 10. Заключение

Спроектированная схема БД обеспечивает:

✅ **Гибкость** — JSON-поля для расширения без миграций
✅ **Производительность** — правильные индексы и FTS
✅ **Масштабируемость** — от SQLite к PostgreSQL
✅ **Безопасность** — шифрование и аудит
✅ **Надежность** — бэкапы и soft deletes
✅ **Интеграцию** — связь с Git через таблицу commits

Схема покрывает все основные требования InGit и готова для реализации MVP.

---

**Версия**: 1.0
**Дата**: 2026-02-01
**Статус**: Ready for implementation
