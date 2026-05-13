from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.performance import ScoutNoteRead
from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate
from app.schemas.player_extras import PlayerClipsRead, PlayerPassportRead, PlayerPerformancesRead
from app.services import api_service

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=list[PlayerRead])
def list_players(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> list[PlayerRead]:
    return api_service.list_players(session, current_user.organization_id)


@router.post("", response_model=PlayerRead)
def create_player(payload: PlayerCreate, session: Session = Depends(get_session)) -> PlayerRead:
    return api_service.create_player(session, payload)


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int, session: Session = Depends(get_session)) -> PlayerRead:
    return api_service.get_player(session, player_id)


@router.patch("/{player_id}", response_model=PlayerRead)
def patch_player(player_id: int, payload: PlayerUpdate, session: Session = Depends(get_session)) -> PlayerRead:
    return api_service.update_player(session, player_id, payload)


@router.get("/{player_id}/passport", response_model=PlayerPassportRead)
def player_passport(player_id: int, session: Session = Depends(get_session)) -> PlayerPassportRead:
    return PlayerPassportRead(**api_service.player_passport(session, player_id))


@router.get("/{player_id}/performances", response_model=PlayerPerformancesRead)
def player_perfs(player_id: int, session: Session = Depends(get_session)) -> PlayerPerformancesRead:
    return PlayerPerformancesRead(items=api_service.player_performances(session, player_id))


@router.get("/{player_id}/clips", response_model=PlayerClipsRead)
def player_clips(player_id: int, session: Session = Depends(get_session)) -> PlayerClipsRead:
    return PlayerClipsRead(items=api_service.player_clips(session, player_id))


@router.get("/{player_id}/scout-notes", response_model=list[ScoutNoteRead])
def player_scout_notes(player_id: int, session: Session = Depends(get_session)) -> list[ScoutNoteRead]:
    return api_service.list_player_scout_notes(session, player_id)
