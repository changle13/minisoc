from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Incident, IncidentAlert

CORRELATION_WINDOW_MINUTES = 10
SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def _max_severity(alerts: list[Alert]) -> str:
    return max((alert.severity for alert in alerts), key=lambda s: SEVERITY_RANK.get(s, 0))


def correlate_incidents(db: Session, alerts: list[Alert]) -> list[Incident]:
    triggered: list[Incident] = []
    triggered_ids: set[int] = set()

    for alert in alerts:
        window_start = alert.last_seen - timedelta(minutes=CORRELATION_WINDOW_MINUTES)
        related_alerts = db.scalars(
            select(Alert)
            .where(
                Alert.entity == alert.entity,
                Alert.last_seen >= window_start,
                Alert.last_seen <= alert.last_seen,
            )
            .order_by(Alert.last_seen)
        ).all()

        if len(related_alerts) < 2:
            continue

        related_ids = [related.id for related in related_alerts]
        incident = db.scalar(
            select(Incident)
            .join(IncidentAlert, IncidentAlert.incident_id == Incident.id)
            .where(IncidentAlert.alert_id.in_(related_ids))
            .limit(1)
        )

        if incident is None:
            incident = Incident(
                title=f"Multiple alerts for {alert.entity}",
                severity=_max_severity(related_alerts),
                status="open",
            )
            db.add(incident)
            db.flush()
        else:
            incident.severity = _max_severity(related_alerts)

        for related_alert in related_alerts:
            if db.get(IncidentAlert, (incident.id, related_alert.id)) is None:
                db.add(
                    IncidentAlert(
                        incident_id=incident.id,
                        alert_id=related_alert.id,
                    )
                )

        if incident.id not in triggered_ids:
            triggered.append(incident)
            triggered_ids.add(incident.id)

    return triggered
