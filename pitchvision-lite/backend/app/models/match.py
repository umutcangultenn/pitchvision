from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SAEnum
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin
from app.models.enums import MatchStatus, VideoSource


class Match(TimestampMixin, SQLModel, table=True):
    __tablename__ = "match"

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id", index=True)
    team_id: int = Field(foreign_key="team.id", index=True)

    opponent_name: str = Field(max_length=255)
    match_date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    age_category: str = Field(max_length=32)
    game_format: str = Field(max_length=32)
    pitch_length: float
    pitch_width: float
    first_half_attack_direction: str = Field(max_length=32)

    score_for: int = Field(default=0, ge=0)
    score_against: int = Field(default=0, ge=0)

    video_source: VideoSource = Field(
        sa_column=Column(
            SAEnum(
                VideoSource,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=32,
            ),
            nullable=False,
        )
    )
    status: MatchStatus = Field(
        sa_column=Column(
            SAEnum(
                MatchStatus,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=32,
            ),
            nullable=False,
        )
    )
