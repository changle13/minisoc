from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    timestamp: datetime
    source_type: str = Field(min_length=1, max_length=32)
    host: str | None = None
    username: str | None = None
    src_ip: str | None = None
    process: str | None = None
    command_line: str | None = None
    raw: dict[str, Any]


class EventBatch(BaseModel):
    events: list[EventIn] = Field(min_length=1, max_length=1000)


class IngestResponse(BaseModel):
    accepted: int
    alerts_triggered: int = 0
