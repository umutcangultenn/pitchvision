from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


class Player(TimestampMixin, SQLModel, table=True):
    __tablename__ = "player"

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id", index=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", index=True)

    first_name: str = Field(max_length=128)
    last_name: str = Field(max_length=128)
    birth_date: date
    position: str = Field(max_length=32)
    dominant_foot: str = Field(max_length=16)
    height_cm: Optional[float] = Field(default=None)
    weight_kg: Optional[float] = Field(default=None)
    photo_url: Optional[str] = Field(default=None, max_length=1024)

    technical_score: Optional[float] = Field(default=None)
    tactical_score: Optional[float] = Field(default=None)
    physical_score: Optional[float] = Field(default=None)
    decision_score: Optional[float] = Field(default=None)
    development_velocity: Optional[float] = Field(default=None)
