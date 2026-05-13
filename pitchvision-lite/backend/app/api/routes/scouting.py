from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.performance import ScoutNoteCreate, ScoutNoteRead
from app.schemas.player import PlayerRead
from app.services import api_service

router = APIRouter(prefix="/scouting", tags=["scouting"])


@router.get("/players", response_model=list[PlayerRead])
def scouting_players(session: Session = Depends(get_session)) -> list[PlayerRead]:
    return api_service.list_scouting_players(session)


@router.get("/hidden-gems", response_model=list[PlayerRead])
def hidden_gems(session: Session = Depends(get_session)) -> list[PlayerRead]:
    return api_service.hidden_gems(session)


@router.post("/notes", response_model=ScoutNoteRead)
def create_note(payload: ScoutNoteCreate, session: Session = Depends(get_session)) -> ScoutNoteRead:
    return api_service.create_scout_note(session, payload)


@router.get("/players/{player_id}/scout-notes", response_model=list[ScoutNoteRead])
def player_notes(player_id: int, session: Session = Depends(get_session)) -> list[ScoutNoteRead]:
    return api_service.list_player_scout_notes(session, player_id)
