from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date
from app.database import get_session
from app.models.user import User
from app.models.player import Player, PlayerCreate, PlayerRead, PlayerUpdate
from app.auth import get_current_active_user

router = APIRouter(prefix="/players", tags=["players"])


@router.post("", response_model=PlayerRead, status_code=201)
def create_player(
    player_create: PlayerCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new player"""
    db_player = Player(**player_create.model_dump())
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    
    # Calculate age
    today = date.today()
    age = today.year - db_player.birth_date.year - (
        (today.month, today.day) < (db_player.birth_date.month, db_player.birth_date.day)
    )
    
    player_dict = db_player.model_dump()
    player_dict["age"] = age
    return PlayerRead(**player_dict)


@router.get("", response_model=List[PlayerRead])
def list_players(
    team_id: int = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """List players"""
    statement = select(Player)
    if team_id:
        statement = statement.where(Player.team_id == team_id)
    players = session.exec(statement).all()
    
    result = []
    today = date.today()
    for player in players:
        age = today.year - player.birth_date.year - (
            (today.month, today.day) < (player.birth_date.month, player.birth_date.day)
        )
        player_dict = player.model_dump()
        player_dict["age"] = age
        result.append(PlayerRead(**player_dict))
    
    return result


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get player by ID"""
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")
    
    today = date.today()
    age = today.year - player.birth_date.year - (
        (today.month, today.day) < (player.birth_date.month, player.birth_date.day)
    )
    
    player_dict = player.model_dump()
    player_dict["age"] = age
    return PlayerRead(**player_dict)


@router.patch("/{player_id}", response_model=PlayerRead)
def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update player"""
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")
    
    update_data = player_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(player, key, value)
    
    session.add(player)
    session.commit()
    session.refresh(player)
    
    return player


@router.delete("/{player_id}", status_code=204)
def delete_player(
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete player"""
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")
    
    session.delete(player)
    session.commit()
    return None
