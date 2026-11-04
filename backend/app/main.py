import logging

from fastapi import FastAPI

from app.core.config import settings
from app.db import check_postgres, check_redis

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    postgres_status = "ok"
    redis_status = "ok"

    try:
        check_postgres()
    except Exception:
        logger.exception("PostgreSQL health check failed")
        postgres_status = "error"

    try:
        check_redis()
    except Exception:
        logger.exception("Redis health check failed")
        redis_status = "error"

    overall = "ok" if postgres_status == "ok" and redis_status == "ok" else "degraded"
    return {"status": overall, "postgres": postgres_status, "redis": redis_status}


@app.get("/api/v1/ping")
def ping() -> dict[str, str]:
    return {"message": "pong", "service": settings.app_name}
