from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class PlayerPosition(str, Enum):
    GK = "Kaleci"
    DF = "Defans"
    MF = "Orta Saha"
    FW = "Forvet"


class PlayerBase(SQLModel):
    jersey_number: int
    full_name: str
    birth_date: date
    position: PlayerPosition
    preferred_foot: str = "Sağ"  # Sağ, Sol, İki Ayak
    height: Optional[int] = None  # cm
    weight: Optional[int] = None  # kg
    photo_url: Optional[str] = None
    notes: Optional[str] = None

    # Development & scouting scores (0-10)
    technical_score: Optional[float] = None
    tactical_score: Optional[float] = None
    physical_score: Optional[float] = None
    decision_score: Optional[float] = None
    development_velocity: Optional[float] = None  # score change per week


class Player(PlayerBase, table=True):
    __tablename__ = "players"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    team: "Team" = Relationship(back_populates="players")
    metrics: List["PlayerMetric"] = Relationship(back_populates="player")


class PlayerCreate(PlayerBase):
    team_id: int


class PlayerRead(PlayerBase):
    id: int
    team_id: int
    created_at: datetime
    age: Optional[int] = None


class PlayerUpdate(SQLModel):
    jersey_number: Optional[int] = None
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    position: Optional[PlayerPosition] = None
    preferred_foot: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    technical_score: Optional[float] = None
    tactical_score: Optional[float] = None
    physical_score: Optional[float] = None
    decision_score: Optional[float] = None
    development_velocity: Optional[float] = None
