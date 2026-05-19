"""
Engine Events API endpoints.
Provides access to AI-detected tactical moments.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from ..database import get_session
from ..auth import get_current_active_user
from ..models.user import User
from ..models.engine_event import EngineEvent, EngineEventRead, EngineEventReview, AnalystVerdict
from ..engine.analyst_workflow import review_engine_event

router = APIRouter(prefix="/engine-events", tags=["engine-events"])


@router.get("/{match_id}", response_model=List[EngineEventRead])
def get_engine_events_for_match(
    match_id: int,
    segment_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all engine-detected events for a match, optionally filtered by segment."""
    query = select(EngineEvent).where(EngineEvent.match_id == match_id)
    
    if segment_id is not None:
        query = query.where(EngineEvent.segment_id == segment_id)
        
    query = query.order_by(EngineEvent.timestamp_seconds)
    return session.exec(query).all()


@router.patch("/{event_id}/review", response_model=EngineEventRead)
def review_event(
    event_id: int,
    review: EngineEventReview,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Review an AI-detected engine event (Analyst validation workflow)."""
    try:
        verdict = AnalystVerdict(review.verdict)
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz verdict değeri")
        
    updated_event = review_engine_event(
        session=session,
        engine_event_id=event_id,
        analyst_id=current_user.id,
        verdict=verdict,
        notes=review.notes
    )
    
    if not updated_event:
        raise HTTPException(status_code=404, detail="Olay bulunamadı")
        
    return updated_event
