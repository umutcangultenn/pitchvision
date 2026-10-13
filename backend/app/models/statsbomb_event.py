"""
StatsBomb Event model.
Stores raw StatsBomb open-data events linked to a match.
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime


class StatsBombEventBase(SQLModel):
    """Core StatsBomb event fields."""
    statsbomb_id: str = Field(index=True)          # UUID from StatsBomb
    event_index: int                                # ordering within match
    period: int                                     # 1 or 2
    timestamp_str: str                              # "00:12:34.567"
    timestamp_seconds: float                        # computed seconds
    minute: int
    second: int
    event_type: str                                 # "Pass", "Shot", etc.
    possession: int                                 # possession sequence number
    possession_team_id: Optional[int] = None
    possession_team_name: Optional[str] = None
    play_pattern: Optional[str] = None
    player_id: Optional[int] = None
    player_name: Optional[str] = None
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    position: Optional[str] = None
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    duration: Optional[float] = None
    # Full raw event payload for advanced queries
    raw_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class StatsBombEvent(StatsBombEventBase, table=True):
    __tablename__ = "statsbomb_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id", index=True)
    statsbomb_match_id: int = Field(index=True)    # original StatsBomb match_id
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StatsBombEventCreate(StatsBombEventBase):
    match_id: int
    statsbomb_match_id: int


class StatsBombEventRead(StatsBombEventBase):
    id: int
    match_id: int
    statsbomb_match_id: int
    created_at: datetime
