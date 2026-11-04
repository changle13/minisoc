from redis import Redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def check_postgres() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def check_redis() -> None:
    if not redis_client.ping():
        raise RuntimeError("Redis ping failed")
