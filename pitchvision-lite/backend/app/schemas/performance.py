from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.base import ReadBase


class PlayerMatchPerformanceCreate(BaseModel):
    player_id: int
    match_id: int
    minutes_played: Optional[float] = None
    average_position_x: Optional[float] = None
    average_position_y: Optional[float] = None
    max_speed: Optional[float] = None
    average_speed: Optional[float] = None
    tactical_score: Optional[float] = None
    technical_score: Optional[float] = None
    physical_score: Optional[float] = None
    decision_score: Optional[float] = None
    alerts_involved: Optional[int] = None
    positive_actions: Optional[int] = None
    development_notes: Optional[str] = None


class PlayerMatchPerformanceUpdate(BaseModel):
    player_id: Optional[int] = None
    match_id: Optional[int] = None
    minutes_played: Optional[float] = None
    average_position_x: Optional[float] = None
    average_position_y: Optional[float] = None
    max_speed: Optional[float] = None
    average_speed: Optional[float] = None
    tactical_score: Optional[float] = None
    technical_score: Optional[float] = None
    physical_score: Optional[float] = None
    decision_score: Optional[float] = None
    alerts_involved: Optional[int] = None
    positive_actions: Optional[int] = None
    development_notes: Optional[str] = None


class PlayerMatchPerformanceRead(ReadBase):
    player_id: int
    match_id: int
    minutes_played: Optional[float]
    average_position_x: Optional[float]
    average_position_y: Optional[float]
    max_speed: Optional[float]
    average_speed: Optional[float]
    tactical_score: Optional[float]
    technical_score: Optional[float]
    physical_score: Optional[float]
    decision_score: Optional[float]
    alerts_involved: Optional[int]
    positive_actions: Optional[int]
    development_notes: Optional[str]


class ScoutNoteCreate(BaseModel):
    player_id: int
    scout_id: int
    note: str
    rating: Optional[float] = Field(default=None, ge=0, le=10)
    tags_json: Optional[dict[str, Any]] = None


class ScoutNoteUpdate(BaseModel):
    player_id: Optional[int] = None
    scout_id: Optional[int] = None
    note: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=10)
    tags_json: Optional[dict[str, Any]] = None


class ScoutNoteRead(ReadBase):
    player_id: int
    scout_id: int
    note: str
    rating: Optional[float]
    tags_json: Optional[dict[str, Any]]
