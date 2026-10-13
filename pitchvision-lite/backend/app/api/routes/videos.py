from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.common_api import DictResponse
from app.schemas.video import VideoAssetCreate, VideoAssetRead
from app.services import api_service
from app.services.access_control import assert_org_access, require_coach_or_above

router = APIRouter(tags=["videos"])


@router.post("/matches/{match_id}/video", response_model=VideoAssetRead)
def upload_video(
    match_id: int, 
    payload: VideoAssetCreate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> VideoAssetRead:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    require_coach_or_above(current_user)
    
    payload.match_id = match_id
    return api_service.upload_video(session, payload)


@router.get("/matches/{match_id}/video", response_model=VideoAssetRead)
def get_video(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> VideoAssetRead:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    
    item = api_service.get_match_video(session, match_id)
    if not item:
        raise api_service._not_found("Video")
    return item


@router.get("/matches/{match_id}/processing-status", response_model=DictResponse)
def processing_status(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> DictResponse:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    
    item = api_service.get_match_video(session, match_id)
    return DictResponse(data={"status": item.status if item else "not_uploaded"})


@router.post("/matches/{match_id}/process", response_model=DictResponse)
def process_video(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> DictResponse:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    require_coach_or_above(current_user)
    
    item = api_service.set_video_processing(session, match_id)
    api_service.start_match_processing(session, match_id)
    return DictResponse(data={"video_status": item.status, "message": "İşleme başlatıldı"})
