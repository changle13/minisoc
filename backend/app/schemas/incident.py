from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.alert import AlertOut


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    severity: str
    status: str
    assignee: str | None = None
    created_at: datetime
    updated_at: datetime


class IncidentDetail(IncidentOut):
    alerts: list[AlertOut]


class IncidentListResponse(BaseModel):
    total: int
    items: list[IncidentOut]
