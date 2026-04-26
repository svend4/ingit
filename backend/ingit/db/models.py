"""
SQLAlchemy ORM Models
Based on DATABASE_SPEC.md
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Date, Boolean,
    ForeignKey, Text, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from ingit.db.base import Base


def generate_uuid():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    avatar_url = Column(String)

    # 2FA
    totp_secret = Column(String)
    totp_enabled = Column(Boolean, default=False)

    # Role and status
    role = Column(String, nullable=False, default="developer")
    status = Column(String, nullable=False, default="active")

    # Metadata
    preferences = Column(Text)  # JSON
    metadata = Column(Text)  # JSON

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    deleted_at = Column(DateTime)

    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('owner', 'admin', 'developer', 'viewer')", name='check_user_role'),
        CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='check_user_status'),
        Index('idx_users_status', 'status'),
    )

    # Relationships
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    reported_tasks = relationship("Task", back_populates="reporter", foreign_keys="Task.reporter_id")


class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)

    # Owner
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    owner_type = Column(String, nullable=False, default="user")

    # Status and visibility
    status = Column(String, nullable=False, default="active")
    visibility = Column(String, nullable=False, default="private")

    # Dates
    start_date = Column(Date)
    end_date = Column(Date)

    # Finance
    budget = Column(Float)
    currency = Column(String, default="USD")

    # Configuration
    default_branch = Column(String, default="main")
    settings = Column(Text)  # JSON

    # Metadata
    metadata = Column(Text)  # JSON

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Constraints
    __table_args__ = (
        CheckConstraint("owner_type IN ('user', 'team')", name='check_owner_type'),
        CheckConstraint("status IN ('active', 'archived', 'suspended')", name='check_project_status'),
        CheckConstraint("visibility IN ('private', 'internal', 'public')", name='check_visibility'),
        Index('idx_projects_owner', 'owner_id', 'owner_type'),
        Index('idx_projects_status', 'status'),
    )

    # Relationships
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    repositories = relationship("Repository", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    financial_records = relationship("FinancialRecord", back_populates="project", cascade="all, delete-orphan")


class Repository(Base):
    """Git Repository model"""
    __tablename__ = "repositories"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Paths
    name = Column(String, nullable=False)
    path = Column(String, unique=True, nullable=False, index=True)

    # Git info
    default_branch = Column(String, default="main")
    remote_url = Column(String)

    # Statistics
    size_bytes = Column(Integer, default=0)
    commit_count = Column(Integer, default=0)
    last_commit_sha = Column(String)
    last_commit_at = Column(DateTime)

    # Metadata
    metadata = Column(Text)  # JSON

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relationships
    project = relationship("Project", back_populates="repositories")
    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Identification
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)

    # Type and status
    type = Column(String, nullable=False, default="task")
    status = Column(String, nullable=False, default="backlog")
    priority = Column(String, nullable=False, default="medium")

    # Assignment
    assignee_id = Column(String, ForeignKey("users.id"))
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Time
    start_date = Column(Date)
    due_date = Column(Date)
    estimated_hours = Column(Float)
    actual_hours = Column(Float, default=0)

    # Hierarchy
    parent_task_id = Column(String, ForeignKey("tasks.id"))
    epic_id = Column(String, ForeignKey("tasks.id"))

    # Metadata
    labels = Column(Text)  # JSON array
    metadata = Column(Text)  # JSON

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    deleted_at = Column(DateTime)

    # Constraints
    __table_args__ = (
        CheckConstraint("type IN ('task', 'bug', 'feature', 'epic', 'subtask')", name='check_task_type'),
        CheckConstraint(
            "status IN ('backlog', 'todo', 'in_progress', 'review', 'blocked', 'done', 'cancelled')",
            name='check_task_status'
        ),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name='check_task_priority'),
        Index('idx_tasks_project', 'project_id'),
        Index('idx_tasks_assignee', 'assignee_id'),
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_parent', 'parent_task_id'),
    )

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    reporter = relationship("User", back_populates="reported_tasks", foreign_keys=[reporter_id])
    parent_task = relationship("Task", remote_side=[id], foreign_keys=[parent_task_id])


class Document(Base):
    """Document model"""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="SET NULL"))

    # Identification
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False, index=True)

    # Type
    type = Column(String, nullable=False, default="general")

    # YAML metadata
    yaml_metadata = Column(Text)  # Full YAML as JSON

    # Extracted fields for indexing
    document_date = Column(Date)
    parties = Column(Text)  # JSON array
    amount = Column(Float)
    currency = Column(String)
    valid_from = Column(Date)
    valid_until = Column(Date)
    document_status = Column(String)

    # Files
    attached_files = Column(Text)  # JSON array of paths
    checksum = Column(String)  # SHA256

    # Metadata
    tags = Column(Text)  # JSON array
    metadata = Column(Text)  # JSON

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relationships
    project = relationship("Project", back_populates="documents")
    repository = relationship("Repository")


class FinancialRecord(Base):
    """Financial Record model"""
    __tablename__ = "financial_records"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Type
    type = Column(String, nullable=False)
    category = Column(String, nullable=False)

    # Amount
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")

    # Description
    title = Column(String, nullable=False)
    description = Column(Text)

    # Date
    transaction_date = Column(Date, nullable=False)

    # Relations
    task_id = Column(String, ForeignKey("tasks.id", ondelete="SET NULL"))
    document_id = Column(String, ForeignKey("documents.id", ondelete="SET NULL"))

    # Payment info
    payment_method = Column(String)
    receipt_path = Column(String)

    # Metadata
    metadata = Column(Text)  # JSON

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Constraints
    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense', 'budget', 'forecast')", name='check_finance_type'),
        Index('idx_finance_project', 'project_id'),
        Index('idx_finance_type', 'type'),
        Index('idx_finance_date', 'transaction_date'),
        Index('idx_finance_category', 'category'),
    )

    # Relationships
    project = relationship("Project", back_populates="financial_records")
    task = relationship("Task")
    document = relationship("Document")


class Commit(Base):
    """Git Commit model"""
    __tablename__ = "commits"

    id = Column(String, primary_key=True, default=generate_uuid)
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)

    # Git data
    sha = Column(String, unique=True, nullable=False, index=True)
    message = Column(Text, nullable=False)
    author_name = Column(String, nullable=False)
    author_email = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))

    commit_date = Column(DateTime, nullable=False)

    # Statistics
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)

    # Relations
    task_ids = Column(Text)  # JSON array of task IDs

    # Metadata
    metadata = Column(Text)  # JSON

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    repository = relationship("Repository", back_populates="commits")
    author = relationship("User")


# Create all tables
def create_tables():
    """Create all database tables"""
    from ingit.db.base import engine
    Base.metadata.create_all(bind=engine)
