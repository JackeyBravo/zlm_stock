from functools import lru_cache
from typing import Literal, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application configuration."""

    api_v1_prefix: str = "/api"
    project_name: str = "ZhunLeMe"
    environment: Literal["local", "dev", "staging", "prod"] = "local"

    database_url: str = "sqlite+aiosqlite:///./data/zlm.db"
    redis_url: str = "redis://localhost:6379/0"

    akshare_base_url: str = "https://akshare.xyz"

    quota_guest_per_day: int = 3
    quota_login_per_day: int = 20

    class Config:
        env_prefix = "ZLM_"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Cache Settings to avoid re-reading environment variables."""
    return Settings()

