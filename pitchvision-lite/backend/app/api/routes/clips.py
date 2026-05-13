from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.tactical import ClipCreate, ClipRead
from app.services import api_service

router = APIRouter(tags=["clips"])


@router.get("/matches/{match_id}/clips", response_model=list[ClipRead])
def list_match_clips(match_id: int, session: Session = Depends(get_session)) -> list[ClipRead]:
    return api_service.list_clips_by_match(session, match_id)


@router.post("/matches/{match_id}/clips", response_model=ClipRead)
def create_match_clip(match_id: int, payload: ClipCreate, session: Session = Depends(get_session)) -> ClipRead:
    payload.match_id = match_id
    return api_service.create_clip(session, payload)


@router.get("/clips/{clip_id}", response_model=ClipRead)
def get_clip(clip_id: int, session: Session = Depends(get_session)) -> ClipRead:
    return api_service.get_clip(session, clip_id)
