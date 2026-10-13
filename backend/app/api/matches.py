from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.user import User
from app.models.match import Match, MatchCreate, MatchRead, MatchUpdate
from app.auth import get_current_active_user
import redis
from app.config import settings
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matches", tags=["matches"])
redis_client = redis.from_url(settings.REDIS_URL)


class VideoURLRequest(BaseModel):
    """Request body for video URL upload"""
    url: str
    title: str = None


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
    """Upload match video from file"""
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Maç bulunamadı")
    
    # Save file
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Update match with video path
    match.video_url = file_path
    session.add(match)
    session.commit()
    
    # Queue analysis job
    redis_client.rpush("analysis_queue", match_id)
    
    return {"message": "Video yüklendi, analiz başlatıldı", "match_id": match_id}


@router.post("/{match_id}/upload-url")
async def upload_video_from_url(
    match_id: int,
    request: VideoURLRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Upload match video from URL (YouTube, etc.)"""
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Maç bulunamadı")
    
    try:
        from app.cv.video_download import download_video_from_url, is_valid_video_url
        
        if not is_valid_video_url(request.url):
            raise HTTPException(status_code=400, detail="Geçersiz video URL'i")
        
        logger.info(f"Downloading video from URL: {request.url}")
        video_path = download_video_from_url(request.url, settings.UPLOAD_DIR)
        
        # Update match with video path
        match.video_url = video_path
        session.add(match)
        session.commit()
        
        # Queue analysis job
        redis_client.rpush("analysis_queue", match_id)
        
        return {
            "message": "Video indirildi, analiz başlatıldı",
            "match_id": match_id,
            "video_path": video_path
        }
    except Exception as e:
        logger.error(f"Video download failed: {e}")
        raise HTTPException(status_code=400, detail=f"Video indirme başarısız: {str(e)}")
