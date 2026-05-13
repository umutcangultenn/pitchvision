from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.user import User
from app.models.match import Match, MatchCreate, MatchRead, MatchUpdate
from app.auth import get_current_active_user
import redis
from app.config import settings

router = APIRouter(prefix="/matches", tags=["matches"])
redis_client = redis.from_url(settings.REDIS_URL)


@router.post("", response_model=MatchRead, status_code=201)
def create_match(
    match_create: MatchCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new match"""
    db_match = Match(**match_create.model_dump())
    session.add(db_match)
    session.commit()
    session.refresh(db_match)
    return db_match


@router.get("", response_model=List[MatchRead])
def list_matches(
    team_id: int = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """List matches"""
    statement = select(Match)
    if team_id:
        statement = statement.where(Match.team_id == team_id)
    matches = session.exec(statement).all()
    return matches


@router.get("/{match_id}", response_model=MatchRead)
def get_match(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get match by ID"""
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Maç bulunamadı")
    return match


@router.post("/{match_id}/upload")
async def upload_video(
    match_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Upload match video"""
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Maç bulunamadı")
    
    # Queue analysis job
    redis_client.rpush("analysis_queue", match_id)
    
    return {"message": "Video yüklendi, analiz başlatıldı", "match_id": match_id}
