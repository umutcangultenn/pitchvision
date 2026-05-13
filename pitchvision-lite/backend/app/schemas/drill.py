from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.enums import (
    AlertType,
    DrillDifficulty,
    PitchSize,
    ProblemType,
)
from app.schemas.base import ReadBase


class DrillRecommendationCreate(BaseModel):
    alert_type: AlertType
    title: str = Field(max_length=255)
    problem_type: ProblemType
    age_category: str = Field(max_length=32)
    duration_minutes: int = Field(ge=1)
    player_count: int = Field(ge=1)
    pitch_size: PitchSize
    difficulty: DrillDifficulty
    description: Optional[str] = None
    coaching_points_json: Optional[list[dict[str, Any]]] = None


class DrillRecommendationUpdate(BaseModel):
    alert_type: Optional[AlertType] = None
    title: Optional[str] = Field(default=None, max_length=255)
    problem_type: Optional[ProblemType] = None
    age_category: Optional[str] = Field(default=None, max_length=32)
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    player_count: Optional[int] = Field(default=None, ge=1)
    pitch_size: Optional[PitchSize] = None
    difficulty: Optional[DrillDifficulty] = None
    description: Optional[str] = None
    coaching_points_json: Optional[list[dict[str, Any]]] = None


class DrillRecommendationRead(ReadBase):
    alert_type: AlertType
    title: str
    problem_type: ProblemType
    age_category: str
    duration_minutes: int
    player_count: int
    pitch_size: PitchSize
    difficulty: DrillDifficulty
    description: Optional[str]
    coaching_points_json: Optional[list[dict[str, Any]]]
