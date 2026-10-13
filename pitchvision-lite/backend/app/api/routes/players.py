from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.performance import ScoutNoteRead
from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate
from app.schemas.player_extras import PlayerClipsRead, PlayerPassportRead, PlayerPerformancesRead
from app.services import api_service
from app.services.access_control import assert_org_access, require_coach_or_above, require_scout_or_above

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=list[PlayerRead])
def list_players(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> list[PlayerRead]:
    return api_service.list_players(session, current_user.organization_id)


@router.post("", response_model=PlayerRead)
def create_player(
    payload: PlayerCreate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> PlayerRead:
    require_coach_or_above(current_user)
    payload.organization_id = current_user.organization_id
    return api_service.create_player(session, payload)


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(
    player_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> PlayerRead:
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    return player


@router.patch("/{player_id}", response_model=PlayerRead)
def patch_player(
    player_id: int, 
    payload: PlayerUpdate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> PlayerRead:
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    require_coach_or_above(current_user)
    return api_service.update_player(session, player_id, payload)


@router.get("/{player_id}/passport", response_model=PlayerPassportRead)
def player_passport(
    player_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> PlayerPassportRead:
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    return PlayerPassportRead(**api_service.player_passport(session, player_id))


@router.get("/{player_id}/performances", response_model=PlayerPerformancesRead)
def player_perfs(
    player_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> PlayerPerformancesRead:
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    return PlayerPerformancesRead(items=api_service.player_performances(session, player_id))


@router.get("/{player_id}/clips", response_model=PlayerClipsRead)
def player_clips(
    player_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> PlayerClipsRead:
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    return PlayerClipsRead(items=api_service.player_clips(session, player_id))


@router.get("/{player_id}/scout-notes", response_model=list[ScoutNoteRead])
def player_scout_notes(
    player_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[ScoutNoteRead]:
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    require_scout_or_above(current_user)
    return api_service.list_player_scout_notes(session, player_id)
