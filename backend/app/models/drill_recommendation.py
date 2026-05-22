from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class DrillDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DrillProblemType(str, Enum):
    TECHNICAL = "technical"
    TACTICAL = "tactical"
    PHYSICAL = "physical"
    DECISION = "decision"


class DrillRecommendationBase(SQLModel):
    title: str
    description: Optional[str] = None
    alert_type: str                          # maps to AlertType in domain.ts
    problem_type: str                        # DrillProblemType value
    difficulty: str = DrillDifficulty.MEDIUM
    duration_minutes: int = 15
    player_count: Optional[int] = None
    age_category: Optional[str] = None      # e.g. "U15"
    pitch_size: Optional[str] = None        # "full", "half", "small_sided"
    coaching_points_json: Optional[List[Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    instructions: Optional[str] = None
    equipment: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))


class DrillRecommendation(DrillRecommendationBase, table=True):
    __tablename__ = "drill_recommendations"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DrillRecommendationCreate(DrillRecommendationBase):
    pass


class DrillRecommendationRead(DrillRecommendationBase):
    id: int
    created_at: datetime
