"""Application configuration for the runnable MVP scaffold."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings for the runnable MVP slice."""

    env: str = Field(default="development", alias="WOS_ENV")
    log_level: str = Field(default="INFO", alias="WOS_LOG_LEVEL")
    database_path: Path = Field(default=Path("runtime_data/wos_mvp.sqlite3"), alias="WOS_DATABASE_PATH")
    internal_api_key: str = Field(default="change-me", alias="WOS_INTERNAL_API_KEY")
    bind_host: str = Field(default="127.0.0.1", alias="WOS_BIND_HOST")
    bind_port: int = Field(default=8000, alias="WOS_BIND_PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def repo_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def published_bundle_path(self) -> Path:
        return self.repo_root.parent / "examples" / "published_artifact_bundle.json"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings."""

    return Settings()
