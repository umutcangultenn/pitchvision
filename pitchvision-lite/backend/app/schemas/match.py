from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import MatchStatus, VideoSource
from app.schemas.base import ReadBase


class MatchCreate(BaseModel):
    organization_id: int
    team_id: int
    opponent_name: str = Field(max_length=255)
    match_date: datetime
    age_category: str = Field(max_length=32)
    game_format: str = Field(max_length=32)
    pitch_length: float
    pitch_width: float
    first_half_attack_direction: str = Field(max_length=32)
    score_for: int = Field(default=0, ge=0)
    score_against: int = Field(default=0, ge=0)
    video_source: VideoSource
    status: MatchStatus


class MatchUpdate(BaseModel):
    organization_id: Optional[int] = None
    team_id: Optional[int] = None
    opponent_name: Optional[str] = Field(default=None, max_length=255)
    match_date: Optional[datetime] = None
    age_category: Optional[str] = Field(default=None, max_length=32)
    game_format: Optional[str] = Field(default=None, max_length=32)
    pitch_length: Optional[float] = None
    pitch_width: Optional[float] = None
    first_half_attack_direction: Optional[str] = Field(default=None, max_length=32)
    score_for: Optional[int] = Field(default=None, ge=0)
    score_against: Optional[int] = Field(default=None, ge=0)
    video_source: Optional[VideoSource] = None
    status: Optional[MatchStatus] = None


class MatchRead(ReadBase):
    organization_id: int
    team_id: int
    opponent_name: str
    match_date: datetime
    age_category: str
    game_format: str
    pitch_length: float
    pitch_width: float
    first_half_attack_direction: str
    score_for: int
    score_against: int
    video_source: VideoSource
    status: MatchStatus
