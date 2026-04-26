"""
Configuration management for InGit
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "InGit"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./ingit.db"

    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Git
    DEFAULT_BRANCH: str = "main"

    # Storage
    STORAGE_PATH: str = "./storage"
    REPOS_PATH: str = "./storage/repos"
    UPLOADS_PATH: str = "./storage/uploads"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/ingit.log"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
