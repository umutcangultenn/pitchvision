"""
Match Segmentation API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from ..database import get_session
from ..auth import get_current_active_user
from ..models.user import User
from ..models.match_segment import MatchSegment, MatchSegmentRead
from ..engine.segmentation import generate_segments_for_match

router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("/{match_id}", response_model=List[MatchSegmentRead])
def get_match_segments(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all segments for a given match."""
    segments = session.exec(
        select(MatchSegment)
        .where(MatchSegment.match_id == match_id)
        .order_by(MatchSegment.start_time)
    ).all()
    return segments


@router.get("/detail/{segment_id}", response_model=MatchSegmentRead)
def get_segment_detail(
    segment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a single match segment by ID."""
    segment = session.get(MatchSegment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment bulunamadı")
    return segment


@router.post("/{match_id}/generate", response_model=List[MatchSegmentRead])
def generate_segments(
    match_id: int,
    duration_minutes: int = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Generate segments for a match."""
    from ..models.match import Match
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Maç bulunamadı")

    segments = generate_segments_for_match(
        session=session,
        match_id=match_id,
        duration_minutes=duration_minutes or match.duration_minutes,
    )
    return segments
