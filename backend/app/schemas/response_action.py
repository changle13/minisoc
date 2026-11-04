from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResponseActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: int | None = None
    action: str
    target_ip: str
    status: str
    detail: str | None = None
    created_at: datetime


class ResponseActionListResponse(BaseModel):
    total: int
    items: list[ResponseActionOut]
