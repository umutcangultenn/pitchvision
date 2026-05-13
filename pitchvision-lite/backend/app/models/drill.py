from typing import Any, Optional

from sqlalchemy import Column, Enum as SAEnum, JSON
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin
from app.models.enums import (
    AlertType,
    DrillDifficulty,
    PitchSize,
    ProblemType,
)


class DrillRecommendation(TimestampMixin, SQLModel, table=True):
    __tablename__ = "drill_recommendation"

    id: Optional[int] = Field(default=None, primary_key=True)

    alert_type: AlertType = Field(
        sa_column=Column(
            SAEnum(
                AlertType,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=48,
            ),
            nullable=False,
        )
    )
    title: str = Field(max_length=255)
    problem_type: ProblemType = Field(
        sa_column=Column(
            SAEnum(
                ProblemType,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=32,
            ),
            nullable=False,
        )
    )
    age_category: str = Field(max_length=32)
    duration_minutes: int = Field(ge=1)
    player_count: int = Field(ge=1)
    pitch_size: PitchSize = Field(
        sa_column=Column(
            SAEnum(
                PitchSize,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=24,
            ),
            nullable=False,
        )
    )
    difficulty: DrillDifficulty = Field(
        sa_column=Column(
            SAEnum(
                DrillDifficulty,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=16,
            ),
            nullable=False,
        )
    )
    description: Optional[str] = Field(default=None)
    coaching_points_json: Optional[list[dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
