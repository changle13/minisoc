from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.event import EventOut


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_id: str
    rule_name: str
    severity: str
    entity: str
    count: int
    first_seen: datetime
    last_seen: datetime
    status: str
    created_at: datetime
    updated_at: datetime


class AlertDetail(AlertOut):
    events: list[EventOut]


class AlertListResponse(BaseModel):
    total: int
    items: list[AlertOut]
