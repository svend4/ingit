# InGit API Specification

## Обзор

InGit REST API предоставляет доступ к функциям управления проектами, задачами, документами и финансами.

**Base URL**: `http://localhost:8000/api`

**Authentication**: JWT Bearer Token

**Content-Type**: `application/json`

---

## Authentication

### POST /auth/register
Регистрация нового пользователя

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "created_at": "2026-02-01T10:00:00Z"
}
```

### POST /auth/login
Вход в систему

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Projects

### GET /projects
Получить список проектов

**Query Parameters:**
- `status` (optional): `active | archived | suspended`
- `skip` (optional): integer, default 0
- `limit` (optional): integer, default 100

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "E-Commerce Platform",
    "slug": "ecommerce-mvp",
    "description": "MVP for e-commerce platform",
    "status": "active",
    "visibility": "private",
    "budget": 750000,
    "currency": "RUB",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-02-01T14:30:00Z"
  }
]
```

### POST /projects
Создать новый проект

**Request Body:**
```json
{
  "name": "My Project",
  "slug": "my-project",
  "description": "Project description",
  "status": "active",
  "visibility": "private",
  "budget": 100000,
  "currency": "USD"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "My Project",
  ...
}
```

### GET /projects/{project_id}
Получить проект по ID

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "My Project",
  ...
}
```

### PUT /projects/{project_id}
Обновить проект

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "status": "active"
}
```

**Response:** `200 OK`

### DELETE /projects/{project_id}
Удалить проект (soft delete)

**Response:** `204 No Content`

---

## Tasks

### GET /tasks
Получить список задач

**Query Parameters:**
- `project_id` (optional): uuid
- `status` (optional): `backlog | todo | in_progress | review | blocked | done | cancelled`
- `assignee_id` (optional): uuid
- `priority` (optional): `low | medium | high | urgent`
- `skip` (optional): integer
- `limit` (optional): integer

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "number": 1,
    "title": "Implement authentication",
    "description": "...",
    "status": "in_progress",
    "priority": "high",
    "type": "feature",
    "project_id": "uuid",
    "assignee_id": "uuid",
    "reporter_id": "uuid",
    "estimated_hours": 16,
    "actual_hours": 8,
    "due_date": "2026-02-05",
    "labels": ["backend", "security"],
    "created_at": "2026-01-20T09:00:00Z",
    "updated_at": "2026-02-01T16:45:00Z"
  }
]
```

### POST /tasks
Создать задачу

**Request Body:**
```json
{
  "project_id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "status": "backlog",
  "priority": "medium",
  "type": "task",
  "assignee_id": "uuid",
  "estimated_hours": 8
}
```

**Response:** `201 Created`

### GET /tasks/{task_id}
Получить задачу

**Response:** `200 OK`

### PUT /tasks/{task_id}
Обновить задачу

**Request Body:**
```json
{
  "title": "Updated title",
  "status": "in_progress",
  "actual_hours": 4
}
```

**Response:** `200 OK`

### POST /tasks/{task_id}/assign
Назначить задачу

**Request Body:**
```json
{
  "assignee_id": "uuid"
}
```

**Response:** `200 OK`

### POST /tasks/{task_id}/close
Закрыть задачу

**Response:** `200 OK`

---

## Documents

### GET /documents
Получить список документов

**Query Parameters:**
- `project_id` (optional): uuid
- `type` (optional): `contract | spec | report | general`
- `skip` (optional): integer
- `limit` (optional): integer

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "title": "Development Contract",
    "file_path": "30_documents/contracts/contract-001.yaml",
    "type": "contract",
    "document_date": "2026-01-15",
    "document_status": "active",
    "yaml_metadata": {...},
    "created_at": "2026-01-15T10:00:00Z"
  }
]
```

### POST /documents
Создать документ

**Request Body:**
```json
{
  "project_id": "uuid",
  "title": "Document Title",
  "file_path": "path/to/document.yaml",
  "type": "contract",
  "yaml_metadata": {...}
}
```

**Response:** `201 Created`

---

## Financial Records

### GET /finance
Получить финансовые записи

**Query Parameters:**
- `project_id` (required): uuid
- `type` (optional): `income | expense | budget | forecast`
- `category` (optional): string
- `from_date` (optional): date
- `to_date` (optional): date

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "type": "expense",
    "category": "infrastructure",
    "title": "DigitalOcean Hosting",
    "amount": -150.00,
    "currency": "USD",
    "transaction_date": "2026-01-25",
    "payment_method": "bank_card",
    "created_at": "2026-01-25T14:30:00Z"
  }
]
```

### POST /finance
Добавить финансовую запись

**Request Body:**
```json
{
  "project_id": "uuid",
  "type": "expense",
  "category": "hosting",
  "title": "Monthly hosting",
  "amount": -150.00,
  "currency": "USD",
  "transaction_date": "2026-01-25",
  "payment_method": "bank_card"
}
```

**Response:** `201 Created`

### GET /finance/summary
Получить финансовую сводку по проекту

**Query Parameters:**
- `project_id` (required): uuid

**Response:** `200 OK`
```json
{
  "project_id": "uuid",
  "total_income": 225000.00,
  "total_expenses": 13650.00,
  "net_profit": 211350.00,
  "budget": 750000.00,
  "budget_remaining": 736350.00,
  "budget_used_percent": 1.82
}
```

---

## Git Operations

### GET /git/repositories
Список репозиториев

**Response:** `200 OK`

### GET /git/repositories/{repo_id}/commits
История коммитов

**Query Parameters:**
- `branch` (optional): string
- `skip` (optional): integer
- `limit` (optional): integer

**Response:** `200 OK`
```json
[
  {
    "sha": "abc123...",
    "message": "Implement authentication",
    "author_name": "Ivan Petrov",
    "commit_date": "2026-02-01T16:00:00Z",
    "additions": 420,
    "deletions": 85,
    "files_changed": 12
  }
]
```

### GET /git/repositories/{repo_id}/diff
Diff между коммитами

**Query Parameters:**
- `from`: commit sha
- `to`: commit sha

**Response:** `200 OK`

---

## Reports

### GET /reports/summary
Сводка по проекту

**Query Parameters:**
- `project_id` (required): uuid

**Response:** `200 OK`
```json
{
  "project": {...},
  "tasks_summary": {
    "total": 10,
    "backlog": 5,
    "in_progress": 3,
    "done": 2
  },
  "finance_summary": {...},
  "time_summary": {
    "total_estimated": 120,
    "total_actual": 45,
    "progress_percent": 37.5
  }
}
```

### GET /reports/weekly
Еженедельный отчет

**Query Parameters:**
- `project_id` (required): uuid
- `days` (optional): integer, default 7

**Response:** `200 OK`

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- **Limit**: 60 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit`: 60
  - `X-RateLimit-Remaining`: 45
  - `X-RateLimit-Reset`: 1706789400

---

## Pagination

Все list endpoints поддерживают пагинацию:

**Query Parameters:**
- `skip`: number of items to skip
- `limit`: max number of items to return

**Response Headers:**
- `X-Total-Count`: total number of items
- `Link`: pagination links

---

## Versioning

API использует версионирование через URL:
- Current: `/api/v1/...`
- Future: `/api/v2/...`

---

**Документация**: `/api/docs` (Swagger UI)
**ReDoc**: `/api/redoc`
**OpenAPI JSON**: `/api/openapi.json`
