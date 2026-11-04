import hashlib
import hmac
import json
import logging
import time

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Alert, ResponseAction

logger = logging.getLogger(__name__)


def send_action(
    action: str,
    target_ip: str,
    alert_id: int | None,
    reason: str,
) -> dict:
    body = json.dumps(
        {
            "ip": target_ip,
            "alert_id": alert_id,
            "reason": reason,
        }
    ).encode("utf-8")
    timestamp = str(int(time.time()))
    signature = hmac.new(
        settings.response_agent_secret.encode("utf-8"),
        f"{timestamp}.".encode("utf-8") + body,
        hashlib.sha256,
    ).hexdigest()

    response = httpx.post(
        f"{settings.response_agent_url}/{action}",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-MiniSOC-Timestamp": timestamp,
            "X-MiniSOC-Signature": signature,
        },
        timeout=5.0,
    )
    response.raise_for_status()
    return response.json()


def auto_block_alerts(db: Session, alerts: list[Alert]) -> None:
    if not settings.response_enabled:
        return

    for alert in alerts:
        if alert.rule_id != "ssh_bruteforce" or alert.severity != "high":
            continue

        existing = db.scalar(
            select(ResponseAction).where(
                ResponseAction.alert_id == alert.id,
                ResponseAction.action == "block",
                ResponseAction.status.in_(("blocked", "already_blocked", "would_block")),
            )
        )
        if existing is not None:
            continue

        try:
            result = send_action(
                "block",
                alert.entity,
                alert.id,
                reason=f"automatic response for {alert.rule_id}",
            )
            status = str(result.get("result", "unknown"))
            detail = json.dumps(result, ensure_ascii=False)
        except Exception as exc:
            logger.exception("Response agent call failed for alert %s", alert.id)
            status = "error"
            detail = str(exc)

        db.add(
            ResponseAction(
                alert_id=alert.id,
                action="block",
                target_ip=alert.entity,
                status=status,
                detail=detail,
            )
        )
        db.commit()
