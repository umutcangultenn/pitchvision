from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.models.enums import AlertStatus, UserRole
from app.schemas.tactical import TacticalAlertRead, TacticalAlertUpdate
from app.services import api_service
from app.services.access_control import assert_org_access, require_role

router = APIRouter(tags=["alerts"])


@router.get("/matches/{match_id}/alerts", response_model=list[TacticalAlertRead])
def list_alerts(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[TacticalAlertRead]:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    return api_service.list_alerts(session, match_id)


@router.patch("/alerts/{alert_id}", response_model=TacticalAlertRead)
def patch_alert(
    alert_id: int, 
    payload: TacticalAlertUpdate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> TacticalAlertRead:
    alert = api_service.get_alert(session, alert_id)
    match = api_service.get_match(session, alert.match_id)
    assert_org_access(match.organization_id, current_user)
    require_role(current_user, UserRole.ANALYST)
    return api_service.update_alert(session, alert_id, payload)


@router.post("/alerts/{alert_id}/approve", response_model=TacticalAlertRead)
def approve_alert(
    alert_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> TacticalAlertRead:
    alert = api_service.get_alert(session, alert_id)
    match = api_service.get_match(session, alert.match_id)
    assert_org_access(match.organization_id, current_user)
    require_role(current_user, UserRole.COACH)
    return api_service.set_alert_status(session, alert_id, AlertStatus.RESOLVED)


@router.post("/alerts/{alert_id}/reject", response_model=TacticalAlertRead)
def reject_alert(
    alert_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> TacticalAlertRead:
    alert = api_service.get_alert(session, alert_id)
    match = api_service.get_match(session, alert.match_id)
    assert_org_access(match.organization_id, current_user)
    require_role(current_user, UserRole.COACH)
    return api_service.set_alert_status(session, alert_id, AlertStatus.DISMISSED)
