"""Application settings loaded from environment / .env (pydantic-settings)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- core ---
    app_env: Literal["dev", "test", "stand", "prod"] = "dev"
    app_name: str = "AI-Кадровик"
    secret_key: str = Field(default="change-me", min_length=8)
    pdn_master_key: str = "change-me-32-bytes-base64"

    # --- db ---
    database_url: str = "postgresql+psycopg://kadrovik:kadrovik@localhost:5432/kadrovik"
    audit_database_url: str = "postgresql+psycopg://audit_writer:audit@localhost:5432/kadrovik"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # --- redis / celery ---
    redis_url: str = "redis://localhost:6379/0"

    # --- minio ---
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minio"
    minio_secret_key: str = "minio12345"
    minio_bucket: str = "documents"
    minio_secure: bool = False

    # --- documents ---
    soffice_url: str = "http://localhost:2004"
    templates_dir: str = "/templates"

    # --- edo stub ---
    edo_operator: Literal["stub"] = "stub"
    edo_stub_fail_format: bool = False

    # --- autonomy ---
    org_first_30_days_force_a2: bool = True

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()
