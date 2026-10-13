from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.performance import ScoutNoteCreate, ScoutNoteRead
from app.schemas.player import PlayerRead
from app.services import api_service
from app.services.access_control import assert_org_access, require_scout_or_above

router = APIRouter(prefix="/scouting", tags=["scouting"])


@router.get("/players", response_model=list[PlayerRead])
def scouting_players(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[PlayerRead]:
    # In a real app, scouting might be cross-org. For Phase 2, we stick to own org.
    return api_service.list_players(session, current_user.organization_id)


@router.get("/hidden-gems", response_model=list[PlayerRead])
def hidden_gems(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[PlayerRead]:
    # Placeholder: currently returns gems from own org
    players = api_service.list_players(session, current_user.organization_id)
    return [p for p in players if (p.development_velocity or 0) > 0.5]


@router.post("/notes", response_model=ScoutNoteRead)
def create_note(
    payload: ScoutNoteCreate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> ScoutNoteRead:
    require_scout_or_above(current_user)
    player = api_service.get_player(session, payload.player_id)
    assert_org_access(player.organization_id, current_user)
    payload.scout_id = current_user.id
    return api_service.create_scout_note(session, payload)


@router.get("/players/{player_id}/scout-notes", response_model=list[ScoutNoteRead])
def player_notes(
    player_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[ScoutNoteRead]:
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    require_scout_or_above(current_user)
    return api_service.list_player_scout_notes(session, player_id)
