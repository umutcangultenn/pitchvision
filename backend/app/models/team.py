from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class TeamBase(SQLModel):
    name: str
    age_group: str  # U8, U10, U12, U14, U16, U17
    season: str  # 2024-2025
    logo_url: Optional[str] = None
    primary_color: str = "#1E40AF"
    secondary_color: str = "#FFFFFF"


class Team(TeamBase, table=True):
    __tablename__ = "teams"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    owner: "User" = Relationship(back_populates="teams")
    players: List["Player"] = Relationship(back_populates="team")
    matches: List["Match"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int
    owner_id: int
    created_at: datetime
    player_count: Optional[int] = 0
    match_count: Optional[int] = 0


class TeamUpdate(SQLModel):
    name: Optional[str] = None
    age_group: Optional[str] = None
    season: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
