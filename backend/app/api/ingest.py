from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.db import get_db
from app.models import Event
from app.schemas.event import EventBatch, IngestResponse
from app.services.correlation import correlate_incidents
from app.services.detection import detect_ssh_bruteforce

router = APIRouter(
    prefix="/api/v1/ingest",
    tags=["ingest"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/events", response_model=IngestResponse, status_code=202)
def ingest_events(batch: EventBatch, db: Session = Depends(get_db)) -> IngestResponse:
    rows = [Event(**event.model_dump()) for event in batch.events]
    db.add_all(rows)
    db.flush()
    alerts = detect_ssh_bruteforce(db, rows)
    incidents = correlate_incidents(db, alerts)
    db.commit()
    return IngestResponse(
        accepted=len(rows),
        alerts_triggered=len(alerts),
        incidents_triggered=len(incidents),
    )
