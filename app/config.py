from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pydantic import Field, computed_field


class Settings(BaseSettings):
    # Database
    postgres_db: str = Field(default="notifier_db")
    postgres_user: str = Field(default="app_user")
    postgres_password: str = Field(default="secret")
    postgres_host: str = Field(default="localhost")
    postgres_port: str = Field(default="5432")

    # Application
    secret_key: str = Field(default="your-secret-key-change-in-production")
    debug: bool = Field(default=True)
    app_env: str = Field(default="development")

    # Telegram
    telegram_bot_token: str = Field(default="")

    # CORS
    allowed_origins: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"])

    @computed_field
    @property
    def database_url(self) -> str:
        """Compute database URL from components."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()