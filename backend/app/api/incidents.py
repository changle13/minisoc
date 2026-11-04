from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Alert, Incident, IncidentAlert
from app.schemas.alert import AlertOut
from app.schemas.incident import IncidentDetail, IncidentListResponse, IncidentOut

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> IncidentListResponse:
    conditions = []
    if severity:
        conditions.append(Incident.severity == severity)
    if status:
        conditions.append(Incident.status == status)

    total = db.scalar(
        select(func.count()).select_from(Incident).where(*conditions)
    ) or 0
    incidents = db.scalars(
        select(Incident)
        .where(*conditions)
        .order_by(Incident.updated_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return IncidentListResponse(
        total=total,
        items=[IncidentOut.model_validate(incident) for incident in incidents],
    )


@router.get("/{incident_id}", response_model=IncidentDetail)
def get_incident(
    incident_id: int, db: Session = Depends(get_db)
) -> IncidentDetail:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    alerts = db.scalars(
        select(Alert)
        .join(IncidentAlert, IncidentAlert.alert_id == Alert.id)
        .where(IncidentAlert.incident_id == incident_id)
        .order_by(Alert.last_seen.desc())
    ).all()

    base = IncidentOut.model_validate(incident)
    return IncidentDetail(
        **base.model_dump(),
        alerts=[AlertOut.model_validate(alert) for alert in alerts],
    )
