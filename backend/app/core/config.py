from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MiniSOC"
    database_url: str = (
        "postgresql+psycopg://minisoc:minisoc_dev_password@postgres:5432/minisoc"
    )
    redis_url: str = "redis://redis:6379/0"
    api_key: str = "dev-ingest-key"
    jwt_secret: str = "dev-jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    admin_username: str = "admin"
    admin_password: str = "admin_dev_password"
    response_enabled: bool = True
    response_agent_url: str = "http://192.168.65.20:9000"
    response_agent_secret: str = "dev-response-secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
