from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MiniSOC"
    database_url: str = (
        "postgresql+psycopg://minisoc:change-me-db-password@postgres:5432/minisoc"
    )
    redis_url: str = "redis://redis:6379/0"
    api_key: str = "change-me-ingest-key"
    jwt_secret: str = "change-me-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    admin_username: str = "admin"
    admin_password: str = "change-me-admin-password"
    response_enabled: bool = True
    response_agent_url: str = "http://192.168.65.20:9000"
    response_agent_secret: str = "change-me-response-secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
