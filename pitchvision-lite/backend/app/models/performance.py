from typing import Any, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


class PlayerMatchPerformance(TimestampMixin, SQLModel, table=True):
    __tablename__ = "player_match_performance"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    match_id: int = Field(foreign_key="match.id", index=True)

    minutes_played: Optional[float] = Field(default=None)
    average_position_x: Optional[float] = Field(default=None)
    average_position_y: Optional[float] = Field(default=None)
    max_speed: Optional[float] = Field(default=None)
    average_speed: Optional[float] = Field(default=None)

    tactical_score: Optional[float] = Field(default=None)
    technical_score: Optional[float] = Field(default=None)
    physical_score: Optional[float] = Field(default=None)
    decision_score: Optional[float] = Field(default=None)

    alerts_involved: Optional[int] = Field(default=None)
    positive_actions: Optional[int] = Field(default=None)
    development_notes: Optional[str] = Field(default=None)


class ScoutNote(TimestampMixin, SQLModel, table=True):
    __tablename__ = "scout_note"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    scout_id: int = Field(foreign_key="users.id", index=True, description="User (scout)")

    note: str = Field()
    rating: Optional[float] = Field(default=None, ge=0, le=10)
    tags_json: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
