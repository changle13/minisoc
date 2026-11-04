from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db import get_db
from app.models import Alert, AlertEvent, Event
from app.schemas.alert import AlertDetail, AlertListResponse, AlertOut
from app.schemas.event import EventOut

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["alerts"],
    dependencies=[Depends(require_roles("viewer", "analyst", "admin"))],
)


@router.get("", response_model=AlertListResponse)
def list_alerts(
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> AlertListResponse:
    conditions = []
    if severity:
        conditions.append(Alert.severity == severity)
    if status:
        conditions.append(Alert.status == status)

    total = db.scalar(
        select(func.count()).select_from(Alert).where(*conditions)
    ) or 0
    alerts = db.scalars(
        select(Alert)
        .where(*conditions)
        .order_by(Alert.last_seen.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return AlertListResponse(
        total=total,
        items=[AlertOut.model_validate(alert) for alert in alerts],
    )


@router.get("/{alert_id}", response_model=AlertDetail)
def get_alert(alert_id: int, db: Session = Depends(get_db)) -> AlertDetail:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    events = db.scalars(
        select(Event)
        .join(AlertEvent, AlertEvent.event_id == Event.id)
        .where(AlertEvent.alert_id == alert_id)
        .order_by(Event.timestamp)
    ).all()

    base = AlertOut.model_validate(alert)
    return AlertDetail(
        **base.model_dump(),
        events=[EventOut.model_validate(event) for event in events],
    )
