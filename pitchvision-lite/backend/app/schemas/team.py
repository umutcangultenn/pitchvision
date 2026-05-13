from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import ReadBase


class TeamCreate(BaseModel):
    organization_id: int
    name: str = Field(max_length=255)
    age_category: str = Field(max_length=32)
    game_format: str = Field(max_length=32)
    default_formation: str = Field(max_length=32)
    pitch_length: float
    pitch_width: float
    season: str = Field(max_length=32)


class TeamUpdate(BaseModel):
    organization_id: Optional[int] = None
    name: Optional[str] = Field(default=None, max_length=255)
    age_category: Optional[str] = Field(default=None, max_length=32)
    game_format: Optional[str] = Field(default=None, max_length=32)
    default_formation: Optional[str] = Field(default=None, max_length=32)
    pitch_length: Optional[float] = None
    pitch_width: Optional[float] = None
    season: Optional[str] = Field(default=None, max_length=32)


class TeamRead(ReadBase):
    organization_id: int
    name: str
    age_category: str
    game_format: str
    default_formation: str
    pitch_length: float
    pitch_width: float
    season: str
