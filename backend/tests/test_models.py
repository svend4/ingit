"""
Tests for SQLAlchemy models
"""

import pytest
from datetime import datetime, date

from ingit.db.models import User, Project, Task, Document, FinancialRecord


class TestUserModel:
    """Test cases for User model"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User",
            role="developer",
            status="active"
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_unique_username(self, db_session):
        """Test that username must be unique"""
        user1 = User(username="testuser", email="test1@example.com", password_hash="hash")
        user2 = User(username="testuser", email="test2@example.com", password_hash="hash")

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestProjectModel:
    """Test cases for Project model"""

    def test_create_project(self, db_session):
        """Test creating a project"""
        user = User(username="owner", email="owner@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        project = Project(
            name="Test Project",
            slug="test-project",
            description="A test project",
            owner_id=user.id,
            status="active",
            visibility="private",
            budget=100000.0,
            currency="USD"
        )
        db_session.add(project)
        db_session.commit()

        assert project.id is not None
        assert project.name == "Test Project"
        assert project.slug == "test-project"
        assert project.owner_id == user.id

    def test_project_slug_unique(self, db_session):
        """Test that project slug must be unique"""
        user = User(username="owner", email="owner@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        project1 = Project(name="Project 1", slug="same-slug", owner_id=user.id)
        project2 = Project(name="Project 2", slug="same-slug", owner_id=user.id)

        db_session.add(project1)
        db_session.commit()

        db_session.add(project2)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestTaskModel:
    """Test cases for Task model"""

    def test_create_task(self, db_session):
        """Test creating a task"""
        user = User(username="user", email="user@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        project = Project(name="Project", slug="project", owner_id=user.id)
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            number=1,
            title="Test Task",
            description="Task description",
            type="task",
            status="backlog",
            priority="medium",
            reporter_id=user.id,
            estimated_hours=8.0
        )
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.number == 1
        assert task.title == "Test Task"
        assert task.status == "backlog"

    def test_task_assignee_relationship(self, db_session):
        """Test task-assignee relationship"""
        user = User(username="user", email="user@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        project = Project(name="Project", slug="project", owner_id=user.id)
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            number=1,
            title="Task",
            reporter_id=user.id,
            assignee_id=user.id
        )
        db_session.add(task)
        db_session.commit()

        assert task.assignee.username == "user"
        assert task.reporter.username == "user"


class TestDocumentModel:
    """Test cases for Document model"""

    def test_create_document(self, db_session):
        """Test creating a document"""
        user = User(username="user", email="user@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        project = Project(name="Project", slug="project", owner_id=user.id)
        db_session.add(project)
        db_session.commit()

        document = Document(
            project_id=project.id,
            title="Test Document",
            file_path="30_documents/test.yaml",
            type="contract",
            document_date=date(2026, 2, 1)
        )
        db_session.add(document)
        db_session.commit()

        assert document.id is not None
        assert document.title == "Test Document"
        assert document.type == "contract"


class TestFinancialRecordModel:
    """Test cases for FinancialRecord model"""

    def test_create_financial_record(self, db_session):
        """Test creating a financial record"""
        user = User(username="user", email="user@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        project = Project(name="Project", slug="project", owner_id=user.id)
        db_session.add(project)
        db_session.commit()

        record = FinancialRecord(
            project_id=project.id,
            type="expense",
            category="infrastructure",
            title="Hosting",
            amount=-150.0,
            currency="USD",
            transaction_date=date(2026, 2, 1)
        )
        db_session.add(record)
        db_session.commit()

        assert record.id is not None
        assert record.type == "expense"
        assert record.amount == -150.0
        assert record.currency == "USD"
