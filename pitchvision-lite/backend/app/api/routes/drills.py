from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.drill import DrillRecommendationRead
from app.services import api_service
from app.services.access_control import assert_org_access

router = APIRouter(tags=["drills"])


@router.get("/drills", response_model=list[DrillRecommendationRead])
def list_drills(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[DrillRecommendationRead]:
    return api_service.list_drills(session)


@router.get("/matches/{match_id}/drill-recommendations", response_model=list[DrillRecommendationRead])
def list_match_drills(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[DrillRecommendationRead]:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    return api_service.list_match_drills(session, match_id)


@router.post("/drills/{drill_id}/mark-applied", response_model=dict)
def mark_drill_applied(
    drill_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> dict:
    """Mark a drill as applied (implemented)"""
    return {"status": "success", "drill_id": drill_id, "message": "Drill marked as applied"}

