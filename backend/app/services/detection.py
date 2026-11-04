from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, AlertEvent, Event

SSH_BRUTEFORCE_RULE_ID = "ssh_bruteforce"
SSH_BRUTEFORCE_THRESHOLD = 5
SSH_BRUTEFORCE_WINDOW_MINUTES = 5


def detect_ssh_bruteforce(db: Session, events: list[Event]) -> list[Alert]:
    latest_by_ip: dict[str, datetime] = {}
    for event in events:
        if event.source_type != "auth":
            continue
        if (event.raw or {}).get("event_type") != "ssh_failed":
            continue
        if not event.src_ip:
            continue
        previous = latest_by_ip.get(event.src_ip)
        if previous is None or event.timestamp > previous:
            latest_by_ip[event.src_ip] = event.timestamp

    triggered: list[Alert] = []
    for src_ip, latest in latest_by_ip.items():
        window_start = latest - timedelta(minutes=SSH_BRUTEFORCE_WINDOW_MINUTES)
        failed_events = db.scalars(
            select(Event)
            .where(
                Event.source_type == "auth",
                Event.src_ip == src_ip,
                Event.timestamp >= window_start,
                Event.timestamp <= latest,
                Event.raw["event_type"].astext == "ssh_failed",
            )
            .order_by(Event.timestamp)
        ).all()

        if len(failed_events) < SSH_BRUTEFORCE_THRESHOLD:
            continue

        bucket_start = latest.replace(second=0, microsecond=0)
        bucket_start = bucket_start.replace(minute=(bucket_start.minute // 5) * 5)
        dedup_key = f"{SSH_BRUTEFORCE_RULE_ID}:{src_ip}:{bucket_start.isoformat()}"

        alert = db.scalar(select(Alert).where(Alert.dedup_key == dedup_key))
        if alert is None:
            alert = Alert(
                rule_id=SSH_BRUTEFORCE_RULE_ID,
                rule_name="SSH Brute Force",
                severity="high",
                entity=src_ip,
                dedup_key=dedup_key,
                count=len(failed_events),
                first_seen=failed_events[0].timestamp,
                last_seen=failed_events[-1].timestamp,
                status="open",
            )
            db.add(alert)
            db.flush()
        else:
            alert.count = len(failed_events)
            alert.last_seen = failed_events[-1].timestamp

        for failed_event in failed_events:
            if db.get(AlertEvent, (alert.id, failed_event.id)) is None:
                db.add(AlertEvent(alert_id=alert.id, event_id=failed_event.id))

        triggered.append(alert)

    return triggered
