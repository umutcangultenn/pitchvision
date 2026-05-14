from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.common_api import DictResponse
from app.schemas.tactical import TacticalMetricRead
from app.services import api_service
from app.services.access_control import assert_org_access, require_coach_or_above

router = APIRouter(tags=["analytics"])


@router.get("/matches/{match_id}/metrics", response_model=list[TacticalMetricRead])
def list_metrics(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[TacticalMetricRead]:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    return api_service.list_metrics(session, match_id)


@router.post("/matches/{match_id}/metrics/recalculate", response_model=DictResponse)
def recalc_metrics(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> DictResponse:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    require_coach_or_above(current_user)
    metric = api_service.recalculate_metrics(session, match_id)
    return DictResponse(data={"metric_id": metric.id, "status": "recalculated"})
