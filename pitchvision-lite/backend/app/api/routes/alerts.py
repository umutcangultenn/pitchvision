from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.enums import AlertStatus
from app.schemas.tactical import TacticalAlertRead, TacticalAlertUpdate
from app.services import api_service

router = APIRouter(tags=["alerts"])


@router.get("/matches/{match_id}/alerts", response_model=list[TacticalAlertRead])
def list_alerts(match_id: int, session: Session = Depends(get_session)) -> list[TacticalAlertRead]:
    return api_service.list_alerts(session, match_id)


@router.patch("/alerts/{alert_id}", response_model=TacticalAlertRead)
def patch_alert(alert_id: int, payload: TacticalAlertUpdate, session: Session = Depends(get_session)) -> TacticalAlertRead:
    return api_service.update_alert(session, alert_id, payload)


@router.post("/alerts/{alert_id}/approve", response_model=TacticalAlertRead)
def approve_alert(alert_id: int, session: Session = Depends(get_session)) -> TacticalAlertRead:
    return api_service.set_alert_status(session, alert_id, AlertStatus.RESOLVED)


@router.post("/alerts/{alert_id}/reject", response_model=TacticalAlertRead)
def reject_alert(alert_id: int, session: Session = Depends(get_session)) -> TacticalAlertRead:
    return api_service.set_alert_status(session, alert_id, AlertStatus.DISMISSED)
