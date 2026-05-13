from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate
from app.services import api_service

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamRead])
def list_teams(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> list[TeamRead]:
    return api_service.list_teams(session, current_user.organization_id)


@router.post("", response_model=TeamRead)
def create_team(payload: TeamCreate, session: Session = Depends(get_session)) -> TeamRead:
    return api_service.create_team(session, payload)


@router.get("/{team_id}", response_model=TeamRead)
def get_team(team_id: int, session: Session = Depends(get_session)) -> TeamRead:
    return api_service.get_team(session, team_id)


@router.patch("/{team_id}", response_model=TeamRead)
def patch_team(team_id: int, payload: TeamUpdate, session: Session = Depends(get_session)) -> TeamRead:
    return api_service.update_team(session, team_id, payload)
