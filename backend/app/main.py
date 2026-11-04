import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.alerts import router as alerts_router
from app.api.auth import router as auth_router
from app.api.incidents import router as incidents_router
from app.api.ingest import router as ingest_router
from app.core.config import settings
from app.db import SessionLocal, check_postgres, check_redis, init_db
from app.services.users import seed_admin

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_admin(db)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(alerts_router)
app.include_router(incidents_router)


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
