.PHONY: help install dev build test lint format clean docker-build docker-up docker-down migrate

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m  # No Color

help: ## Show this help message
	@echo "$(BLUE)InGit - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Installation
install: ## Install all dependencies (backend + frontend)
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ Installation complete$(NC)"

dev-install: ## Install development dependencies
	@echo "$(BLUE)Installing backend dev dependencies...$(NC)"
	cd backend && pip install -r requirements-dev.txt
	@echo "$(BLUE)Installing frontend dev dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	./scripts/install-hooks.sh
	@echo "$(GREEN)✓ Development setup complete$(NC)"

# Development
dev-backend: ## Run backend in development mode
	@echo "$(BLUE)Starting backend server...$(NC)"
	cd backend && python -m ingit.main

dev-frontend: ## Run frontend in development mode
	@echo "$(BLUE)Starting frontend dev server...$(NC)"
	cd frontend && npm run dev

dev: ## Run both backend and frontend in development mode
	@echo "$(BLUE)Starting InGit development environment...$(NC)"
	@make -j2 dev-backend dev-frontend

# Testing
test: ## Run all tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && pytest
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test

test-backend: ## Run backend tests only
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && pytest

test-frontend: ## Run frontend tests only
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	cd backend && pytest --cov=ingit --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in backend/htmlcov/$(NC)"

# Linting and Formatting
lint: ## Run all linters
	@echo "$(BLUE)Linting backend...$(NC)"
	cd backend && flake8 ingit
	cd backend && black --check ingit
	@echo "$(BLUE)Linting frontend...$(NC)"
	cd frontend && npm run lint
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code (backend + frontend)
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && black ingit
	cd backend && isort ingit
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && npm run format
	@echo "$(GREEN)✓ Code formatted$(NC)"

type-check: ## Run type checkers
	@echo "$(BLUE)Type checking backend...$(NC)"
	cd backend && mypy ingit --ignore-missing-imports
	@echo "$(BLUE)Type checking frontend...$(NC)"
	cd frontend && npm run type-check
	@echo "$(GREEN)✓ Type checking complete$(NC)"

# Database
migrate-create: ## Create a new database migration (usage: make migrate-create m="description")
	@echo "$(BLUE)Creating new migration...$(NC)"
	cd backend && alembic revision --autogenerate -m "$(m)"
	@echo "$(GREEN)✓ Migration created$(NC)"

migrate-up: ## Apply all pending migrations
	@echo "$(BLUE)Applying migrations...$(NC)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Migrations applied$(NC)"

migrate-down: ## Downgrade one migration
	@echo "$(YELLOW)Downgrading migration...$(NC)"
	cd backend && alembic downgrade -1
	@echo "$(GREEN)✓ Migration downgraded$(NC)"

migrate-history: ## Show migration history
	@echo "$(BLUE)Migration history:$(NC)"
	cd backend && alembic history

migrate-current: ## Show current migration
	@echo "$(BLUE)Current migration:$(NC)"
	cd backend && alembic current

# Docker
docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Containers started$(NC)"
	@echo "$(BLUE)Backend API: http://localhost:8000$(NC)"
	@echo "$(BLUE)Frontend: http://localhost:3000$(NC)"
	@echo "$(BLUE)Adminer: http://localhost:8080$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(YELLOW)Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Containers stopped$(NC)"

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-clean: ## Remove Docker containers and volumes
	@echo "$(RED)Removing Docker containers and volumes...$(NC)"
	docker-compose down -v
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# Build
build-backend: ## Build backend for production
	@echo "$(BLUE)Building backend...$(NC)"
	cd backend && python -m build
	@echo "$(GREEN)✓ Backend built$(NC)"

build-frontend: ## Build frontend for production
	@echo "$(BLUE)Building frontend...$(NC)"
	cd frontend && npm run build
	@echo "$(GREEN)✓ Frontend built$(NC)"

build: ## Build both backend and frontend
	@make build-backend
	@make build-frontend
	@echo "$(GREEN)✓ Build complete$(NC)"

# Cleaning
clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/dist backend/build
	rm -rf frontend/dist frontend/build
	rm -rf backend/htmlcov
	rm -rf backend/.coverage
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# Utilities
init-db: ## Initialize database with sample data
	@echo "$(BLUE)Initializing database...$(NC)"
	cd backend && python scripts/init_db.py
	@echo "$(GREEN)✓ Database initialized$(NC)"

generate-report: ## Generate project report
	@echo "$(BLUE)Generating report...$(NC)"
	python scripts/generate-report.py examples/demo-project summary
	@echo "$(GREEN)✓ Report generated$(NC)"

check: lint test ## Run linters and tests

ci: lint test-coverage ## Run CI pipeline (lint + test with coverage)

all: clean install lint test build ## Do everything (clean, install, lint, test, build)

.DEFAULT_GOAL := help
