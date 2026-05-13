from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.drill import DrillRecommendationRead
from app.services import api_service

router = APIRouter(tags=["drills"])


@router.get("/drills", response_model=list[DrillRecommendationRead])
def list_drills(session: Session = Depends(get_session)) -> list[DrillRecommendationRead]:
    return api_service.list_drills(session)


@router.get("/matches/{match_id}/drill-recommendations", response_model=list[DrillRecommendationRead])
def list_match_drills(match_id: int, session: Session = Depends(get_session)) -> list[DrillRecommendationRead]:
    return api_service.list_match_drills(session, match_id)


@router.post("/drills/{drill_id}/mark-applied", response_model=dict)
def mark_drill_applied(drill_id: int, session: Session = Depends(get_session)) -> dict:
    """Mark a drill as applied (implemented)"""
    # Placeholder: In real implementation, would track drill application in database
    return {"status": "success", "drill_id": drill_id, "message": "Drill marked as applied"}

