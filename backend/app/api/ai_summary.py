"""
AI Summary API endpoints.
Provides endpoints to trigger Ollama-powered tactical summarization.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Dict, Any

from ..database import get_session
from ..auth import get_current_active_user
from ..models.user import User
from ..models.match_segment import MatchSegment
from ..models.engine_event import EngineEvent
from ..models.match import Match
from ..engine.ai_summarizer import generate_segment_summary, generate_match_tactical_draft

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/summarize-segment/{segment_id}")
async def summarize_segment(
    segment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Generate AI tactical summary for a single segment."""
    segment = session.get(MatchSegment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment bulunamadı")
        
    events = session.exec(
        select(EngineEvent)
        .where(EngineEvent.segment_id == segment_id)
        .order_by(EngineEvent.timestamp_seconds)
    ).all()
    
    try:
        summary = await generate_segment_summary(segment, list(events))
        
        # Save the summary to the segment
        segment.tactical_summary_ai = summary
        session.add(segment)
        session.commit()
        session.refresh(segment)
        
        return {"segment_id": segment_id, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Özet oluşturulamadı: {str(e)}")


@router.post("/match-summary/{match_id}")
async def summarize_match(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Generate a full match tactical draft."""
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Maç bulunamadı")
        
    segments = session.exec(
        select(MatchSegment)
        .where(MatchSegment.match_id == match_id)
        .order_by(MatchSegment.start_time)
    ).all()
    
    try:
        draft = await generate_match_tactical_draft(
            segments=list(segments),
            team_name=match.team.name if match.team else "Takım",
            opponent_name=match.opponent_name
        )
        return {"match_id": match_id, "draft": draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Maç özeti oluşturulamadı: {str(e)}")


@router.get("/health")
async def check_ai_health():
    """Check connectivity to the NVIDIA NIM API."""
    from ..config import settings
    import httpx

    url = f"{settings.NVIDIA_BASE_URL}/models"
    headers = {"Authorization": f"Bearer {settings.NVIDIA_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return {"status": "online", "provider": "NVIDIA NIM", "model": settings.NVIDIA_MODEL}
    except Exception as e:
        return {"status": "offline", "error": str(e)}
