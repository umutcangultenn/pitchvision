"""
Analyst Events API endpoints.
Provides manual tagging capabilities for the human analyst workflow.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from ..database import get_session
from ..auth import get_current_active_user
from ..models.user import User
from ..models.analyst_event import AnalystEvent, AnalystEventCreate, AnalystEventRead, AnalystEventUpdate
from ..models.match_segment import MatchSegment
from ..engine.analyst_workflow import create_analyst_event, update_analyst_event, get_analyst_events_for_match

router = APIRouter(prefix="/analyst-events", tags=["analyst-events"])


@router.get("/{match_id}", response_model=List[AnalystEventRead])
def get_events(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all manual analyst events for a match."""
    return get_analyst_events_for_match(session, match_id)


@router.post("/", response_model=AnalystEventRead)
def create_event(
    event_in: AnalystEventCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new manual analyst event."""
    # Get segments to auto-assign segment_id if missing
    segments = session.exec(
        select(MatchSegment).where(MatchSegment.match_id == event_in.match_id)
    ).all()
    
    return create_analyst_event(
        session=session,
        event_in=event_in,
        analyst_id=current_user.id,
        segments=list(segments)
    )


@router.patch("/{event_id}", response_model=AnalystEventRead)
def update_event(
    event_id: int,
    event_in: AnalystEventUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update a manual analyst event."""
    try:
        updated = update_analyst_event(
            session=session,
            event_id=event_id,
            event_in=event_in,
            analyst_id=current_user.id
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Olay bulunamadı")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a manual analyst event."""
    event = session.get(AnalystEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Olay bulunamadı")
        
    if event.analyst_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")
        
    session.delete(event)
    session.commit()
    return {"ok": True}
