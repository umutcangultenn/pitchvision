from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.common_api import DictResponse, MessageResponse
from app.schemas.match import MatchCreate, MatchRead, MatchUpdate
from app.services import api_service
from app.services.access_control import assert_org_access, require_coach_or_above

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchRead])
def list_matches(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> list[MatchRead]:
    return api_service.list_matches(session, current_user.organization_id)


@router.post("", response_model=MatchRead)
def create_match(
    payload: MatchCreate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> MatchRead:
    require_coach_or_above(current_user)
    payload.organization_id = current_user.organization_id
    return api_service.create_match(session, payload)


@router.get("/{match_id}", response_model=MatchRead)
def get_match(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> MatchRead:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    return match


@router.patch("/{match_id}", response_model=MatchRead)
def patch_match(
    match_id: int, 
    payload: MatchUpdate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> MatchRead:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    require_coach_or_above(current_user)
    return api_service.update_match(session, match_id, payload)


@router.delete("/{match_id}", response_model=MessageResponse)
def delete_match(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> MessageResponse:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    require_coach_or_above(current_user)
    api_service.delete_match(session, match_id)
    return MessageResponse(message="Maç silindi.")


@router.get("/{match_id}/summary", response_model=DictResponse)
def match_summary(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> DictResponse:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    return DictResponse(data=api_service.match_summary(session, match_id))
