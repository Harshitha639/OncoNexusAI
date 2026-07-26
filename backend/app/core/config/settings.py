"""
Centralized application configuration.

All environment-driven configuration lives here. No module in the
application should read `os.environ` directly — everything flows
through the `Settings` singleton exposed as `settings`.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute path to backend/.env
BACKEND_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application-wide settings, populated from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Project metadata
    # ------------------------------------------------------------------
    PROJECT_NAME: str = "OncoNexus AI"
    PROJECT_DESCRIPTION: str = (
        "A Multi-Agent Intelligent Cancer Care Platform for Risk Assessment, "
        "Medical Report Understanding, Personalized Guidance, Rehabilitation, "
        "and Patient Support using Large Language Models."
    )
    PROJECT_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ------------------------------------------------------------------
    # Security / Auth
    # ------------------------------------------------------------------
    SECRET_KEY: str = Field(default="change-me-in-env", min_length=1)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value):
        if isinstance(value, str) and not value.startswith("["):
            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]
        return value

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    POSTGRES_USER: str = "onconexus"
    POSTGRES_PASSWORD: str = "onconexus"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "onconexus_db"
    DATABASE_ECHO: bool = False

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # ------------------------------------------------------------------
    # AI / ML
    # ------------------------------------------------------------------
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    VECTOR_STORE_DIR: str = "./data/vector_store"
    TRAINED_MODELS_DIR: str = "../trained_models"

    # ------------------------------------------------------------------
    # Gemini
    # ------------------------------------------------------------------
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ------------------------------------------------------------------
    # File uploads
    # ------------------------------------------------------------------
    UPLOAD_DIR: str = "./storage/reports"
    MAX_UPLOAD_SIZE_MB: int = 20
    ALLOWED_REPORT_EXTENSIONS: List[str] = [
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
    ]

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return cached settings."""
    return Settings()


settings = get_settings()