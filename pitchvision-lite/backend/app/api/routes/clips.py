from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.tactical import ClipCreate, ClipRead
from app.services import api_service
from app.services.access_control import assert_org_access, require_coach_or_above

router = APIRouter(tags=["clips"])


@router.get("/matches/{match_id}/clips", response_model=list[ClipRead])
def list_match_clips(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[ClipRead]:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    return api_service.list_clips_by_match(session, match_id)


@router.post("/matches/{match_id}/clips", response_model=ClipRead)
def create_match_clip(
    match_id: int, 
    payload: ClipCreate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> ClipRead:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    require_coach_or_above(current_user)
    payload.match_id = match_id
    return api_service.create_clip(session, payload)


@router.get("/clips/{clip_id}", response_model=ClipRead)
def get_clip(
    clip_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> ClipRead:
    clip = api_service.get_clip(session, clip_id)
    match = api_service.get_match(session, clip.match_id)
    assert_org_access(match.organization_id, current_user)
    return clip
