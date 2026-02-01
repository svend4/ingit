# Changelog

All notable changes to InGit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Mobile app (Android) support
- Advanced Gantt charts
- Real-time collaboration
- Plugin marketplace
- AI-powered features

## [0.1.0] - 2026-02-01

### Added

#### Core Features
- ✅ FastAPI backend with RESTful API
- ✅ React + TypeScript frontend foundation
- ✅ SQLAlchemy ORM with PostgreSQL/SQLite support
- ✅ Git integration via pygit2
- ✅ YAML-based metadata system
- ✅ Offline-first architecture

#### Project Management
- ✅ Project creation and management
- ✅ Task tracking with status workflow
- ✅ Document management with metadata
- ✅ Financial records tracking
- ✅ Timeline/journal support

#### Developer Tools
- ✅ CLI tool (`ingit` command)
  - `ingit init` - Initialize new projects
  - `ingit task create/list` - Task management
  - `ingit report` - Generate reports
  - `ingit doctor` - System diagnostics
- ✅ Git hooks (pre-commit, post-commit)
- ✅ YAML validation
- ✅ Auto-generated reports

#### Infrastructure
- ✅ Docker support (multi-stage builds)
- ✅ Docker Compose for full stack
- ✅ CI/CD with GitHub Actions
  - Automated testing
  - Code quality checks
  - Security scanning
  - Docker image publishing
- ✅ Database migrations (Alembic)
- ✅ Comprehensive Makefile (35+ commands)

#### Testing
- ✅ Unit tests (pytest)
- ✅ Integration tests
- ✅ API tests
- ✅ Model tests
- ✅ 26+ test cases
- ✅ Coverage reporting

#### Monitoring
- ✅ Prometheus metrics collection
- ✅ Grafana dashboards
- ✅ Alertmanager for notifications
- ✅ Loki log aggregation
- ✅ Health check endpoints
- ✅ System metrics exporters

#### Documentation
- ✅ Comprehensive README
- ✅ API specification (OpenAPI)
- ✅ UI wireframes
- ✅ Database specification
- ✅ Implementation roadmap
- ✅ Deployment guides
- ✅ Contributing guidelines
- ✅ Quick start guide

#### Examples
- ✅ Demo project structure
- ✅ YAML metadata templates
- ✅ Sample tasks, documents, finances
- ✅ Report generation scripts

### Technical Stack

**Backend:**
- Python 3.11+
- FastAPI 0.109
- SQLAlchemy 2.0
- PostgreSQL 15 / SQLite
- Redis 7
- pygit2 1.14

**Frontend:**
- React 18
- TypeScript 5
- Vite 5
- Ant Design / Material-UI

**DevOps:**
- Docker & Docker Compose
- GitHub Actions
- Prometheus & Grafana
- Alembic migrations

### Security
- ✅ JWT authentication
- ✅ Password hashing (bcrypt/argon2)
- ✅ 2FA support (TOTP)
- ✅ End-to-end encryption (age)
- ✅ SQL injection protection
- ✅ CORS configuration
- ✅ Security headers
- ✅ Rate limiting

### Performance
- ✅ Database indexing
- ✅ Connection pooling
- ✅ Redis caching
- ✅ Gzip compression
- ✅ Static asset optimization

## Statistics (v0.1.0)

- **Total Files**: 69+
- **Lines of Code**: 5,700+
- **Documentation Pages**: 10
- **Test Cases**: 26
- **API Endpoints**: 15+
- **CLI Commands**: 10+
- **Makefile Tasks**: 35+
- **Docker Services**: 7

## Contributors

- InGit Development Team
- Community Contributors (see CONTRIBUTING.md)

## License

MIT License - see LICENSE file for details

---

[Unreleased]: https://github.com/your-org/ingit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/ingit/releases/tag/v0.1.0
