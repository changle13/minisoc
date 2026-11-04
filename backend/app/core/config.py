from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MiniSOC"
    database_url: str = (
        "postgresql+psycopg://minisoc:minisoc_dev_password@postgres:5432/minisoc"
    )
    redis_url: str = "redis://redis:6379/0"
    api_key: str = "dev-ingest-key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
