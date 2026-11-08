"""Application configuration loaded from environment variables.

Values are read from the environment (optionally via a local `.env` file) so that
the same code runs in local Docker Compose and future deployment environments
without secrets committed to source control.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings for the Aloe backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API
    app_name: str = "Aloe"
    api_v1_prefix: str = "/v1"

    # Database
    postgres_user: str = "aloe"
    postgres_password: str = "aloe"
    postgres_db: str = "aloe"
    postgres_host: str = "localhost"
    postgres_port: int = 5434

    # Market-data service
    mds_source: str = "mock"  # "mock" | "databento"

    @property
    def database_url(self) -> str:
        """SQLAlchemy database URL assembled from individual settings."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so env is parsed once per process."""
    return Settings()
