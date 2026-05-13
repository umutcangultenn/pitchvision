from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.common_api import DictResponse
from app.schemas.track_point import TrackPointCreate
from app.schemas.video import FieldCalibrationCreate, FieldCalibrationRead
from app.services import api_service

router = APIRouter(tags=["calibration"])


@router.post("/matches/{match_id}/calibration", response_model=FieldCalibrationRead)
def create_calibration(
    match_id: int, payload: FieldCalibrationCreate, session: Session = Depends(get_session)
) -> FieldCalibrationRead:
    payload.match_id = match_id
    return api_service.create_calibration(session, payload)


@router.get("/matches/{match_id}/calibration", response_model=FieldCalibrationRead)
def get_calibration(match_id: int, session: Session = Depends(get_session)) -> FieldCalibrationRead:
    item = api_service.get_calibration(session, match_id)
    if not item:
        raise api_service._not_found("Kalibrasyon")
    return item


@router.post("/matches/{match_id}/calibration/test", response_model=DictResponse)
def test_calibration(match_id: int, session: Session = Depends(get_session)) -> DictResponse:
    test_point = TrackPointCreate(
        match_id=match_id,
        player_id=None,
        team_id=None,
        track_id="calib-test",
        frame_index=0,
        event_ts=datetime.now(timezone.utc),
        class_name="ball",
        bbox_json={"x": 1, "y": 1, "w": 10, "h": 10},
        pixel_x=50.0,
        pixel_y=50.0,
        field_x=5.0,
        field_y=5.0,
        confidence=0.99,
    )
    item = api_service.run_calibration_test(session, test_point)
    return DictResponse(data={"track_point_id": item.id, "result": "ok"})
