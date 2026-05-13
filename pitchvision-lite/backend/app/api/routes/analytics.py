from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.common_api import DictResponse
from app.schemas.tactical import TacticalMetricRead
from app.services import api_service

router = APIRouter(tags=["analytics"])


@router.get("/matches/{match_id}/metrics", response_model=list[TacticalMetricRead])
def list_metrics(match_id: int, session: Session = Depends(get_session)) -> list[TacticalMetricRead]:
    return api_service.list_metrics(session, match_id)


@router.post("/matches/{match_id}/metrics/recalculate", response_model=DictResponse)
def recalc_metrics(match_id: int, session: Session = Depends(get_session)) -> DictResponse:
    metric = api_service.recalculate_metrics(session, match_id)
    return DictResponse(data={"metric_id": metric.id, "status": "recalculated"})
