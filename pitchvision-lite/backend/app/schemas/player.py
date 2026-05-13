from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import ReadBase


class PlayerCreate(BaseModel):
    organization_id: int
    team_id: Optional[int] = None
    first_name: str = Field(max_length=128)
    last_name: str = Field(max_length=128)
    birth_date: date
    position: str = Field(max_length=32)
    dominant_foot: str = Field(max_length=16)
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    photo_url: Optional[str] = Field(default=None, max_length=1024)
    technical_score: Optional[float] = None
    tactical_score: Optional[float] = None
    physical_score: Optional[float] = None
    decision_score: Optional[float] = None
    development_velocity: Optional[float] = None


class PlayerUpdate(BaseModel):
    organization_id: Optional[int] = None
    team_id: Optional[int] = None
    first_name: Optional[str] = Field(default=None, max_length=128)
    last_name: Optional[str] = Field(default=None, max_length=128)
    birth_date: Optional[date] = None
    position: Optional[str] = Field(default=None, max_length=32)
    dominant_foot: Optional[str] = Field(default=None, max_length=16)
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    photo_url: Optional[str] = Field(default=None, max_length=1024)
    technical_score: Optional[float] = None
    tactical_score: Optional[float] = None
    physical_score: Optional[float] = None
    decision_score: Optional[float] = None
    development_velocity: Optional[float] = None


class PlayerRead(ReadBase):
    organization_id: int
    team_id: Optional[int]
    first_name: str
    last_name: str
    birth_date: date
    position: str
    dominant_foot: str
    height_cm: Optional[float]
    weight_kg: Optional[float]
    photo_url: Optional[str]
    technical_score: Optional[float]
    tactical_score: Optional[float]
    physical_score: Optional[float]
    decision_score: Optional[float]
    development_velocity: Optional[float]
