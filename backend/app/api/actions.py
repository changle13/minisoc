from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db import get_db
from app.models import ResponseAction
from app.schemas.response_action import ResponseActionListResponse, ResponseActionOut

router = APIRouter(
    prefix="/api/v1/actions",
    tags=["actions"],
    dependencies=[Depends(require_roles("viewer", "analyst", "admin"))],
)


@router.get("", response_model=ResponseActionListResponse)
def list_actions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ResponseActionListResponse:
    total = db.scalar(select(func.count()).select_from(ResponseAction)) or 0
    actions = db.scalars(
        select(ResponseAction)
        .order_by(ResponseAction.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return ResponseActionListResponse(
        total=total,
        items=[ResponseActionOut.model_validate(action) for action in actions],
    )
