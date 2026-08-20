import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Marketing AI Agent"
    environment: str = "development"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://marketing:your_password@localhost:5432/marketing_ai",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()