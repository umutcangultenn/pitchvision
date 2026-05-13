from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.common_api import DictResponse
from app.schemas.video import VideoAssetCreate, VideoAssetRead
from app.services import api_service

router = APIRouter(tags=["videos"])


@router.post("/matches/{match_id}/video", response_model=VideoAssetRead)
def upload_video(match_id: int, payload: VideoAssetCreate, session: Session = Depends(get_session)) -> VideoAssetRead:
    payload.match_id = match_id
    return api_service.upload_video(session, payload)


@router.get("/matches/{match_id}/video", response_model=VideoAssetRead)
def get_video(match_id: int, session: Session = Depends(get_session)) -> VideoAssetRead:
    item = api_service.get_match_video(session, match_id)
    if not item:
        raise api_service._not_found("Video")
    return item


@router.get("/matches/{match_id}/processing-status", response_model=DictResponse)
def processing_status(match_id: int, session: Session = Depends(get_session)) -> DictResponse:
    item = api_service.get_match_video(session, match_id)
    return DictResponse(data={"status": item.status if item else "not_uploaded"})


@router.post("/matches/{match_id}/process", response_model=DictResponse)
def process_video(match_id: int, session: Session = Depends(get_session)) -> DictResponse:
    item = api_service.set_video_processing(session, match_id)
    api_service.start_match_processing(session, match_id)
    return DictResponse(data={"video_status": item.status, "message": "İşleme başlatıldı"})
