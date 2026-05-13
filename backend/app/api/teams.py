from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.user import User
from app.models.team import Team, TeamCreate, TeamRead, TeamUpdate
from app.auth import get_current_active_user

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    team_create: TeamCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new team"""
    db_team = Team(**team_create.model_dump(), owner_id=current_user.id)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    
    return db_team


@router.get("", response_model=List[TeamRead])
def list_teams(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """List all teams for current user"""
    statement = select(Team).where(Team.owner_id == current_user.id)
    teams = session.exec(statement).all()
    
    # Add counts
    result = []
    for team in teams:
        team_dict = team.model_dump()
        team_dict["player_count"] = len(team.players)
        team_dict["match_count"] = len(team.matches)
        result.append(TeamRead(**team_dict))
    
    return result


@router.get("/{team_id}", response_model=TeamRead)
def get_team(
    team_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get team by ID"""
    team = session.get(Team, team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="Takım bulunamadı")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu takıma erişim yetkiniz yok")
    
    team_dict = team.model_dump()
    team_dict["player_count"] = len(team.players)
    team_dict["match_count"] = len(team.matches)
    
    return TeamRead(**team_dict)


@router.patch("/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    team_update: TeamUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update team"""
    team = session.get(Team, team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="Takım bulunamadı")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu takıma erişim yetkiniz yok")
    
    update_data = team_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)
    
    session.add(team)
    session.commit()
    session.refresh(team)
    
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete team"""
    team = session.get(Team, team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail="Takım bulunamadı")
    
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu takıma erişim yetkiniz yok")
    
    session.delete(team)
    session.commit()
    
    return None
