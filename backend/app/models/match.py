from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MatchStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    CALIBRATING = "calibrating"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class MatchBase(SQLModel):
    opponent_name: str
    match_date: datetime
    location: str
    home_away: str = "Ev Sahibi"  # Ev Sahibi, Deplasman
    final_score_home: Optional[int] = None
    final_score_away: Optional[int] = None
    half_time_score_home: Optional[int] = None
    half_time_score_away: Optional[int] = None
    duration_minutes: int = 90
    weather: Optional[str] = None
    notes: Optional[str] = None


class Match(MatchBase, table=True):
    __tablename__ = "matches"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id")
    status: MatchStatus = MatchStatus.PENDING
    video_url: Optional[str] = None
    video_duration: Optional[float] = None  # seconds
    thumbnail_url: Optional[str] = None
    calibration_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    team: "Team" = Relationship(back_populates="matches")
    analysis: Optional["Analysis"] = Relationship(back_populates="match")
    tactical_alerts: List["TacticalAlert"] = Relationship(back_populates="match")


class MatchCreate(MatchBase):
    team_id: int


class MatchRead(MatchBase):
    id: int
    team_id: int
    status: MatchStatus
    video_url: Optional[str]
    video_duration: Optional[float]
    thumbnail_url: Optional[str]
    created_at: datetime
    has_analysis: bool = False


class MatchUpdate(SQLModel):
    opponent_name: Optional[str] = None
    match_date: Optional[datetime] = None
    location: Optional[str] = None
    home_away: Optional[str] = None
    final_score_home: Optional[int] = None
    final_score_away: Optional[int] = None
    half_time_score_home: Optional[int] = None
    half_time_score_away: Optional[int] = None
    status: Optional[MatchStatus] = None
    calibration_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
