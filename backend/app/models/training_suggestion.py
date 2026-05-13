from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TrainingCategory(str, Enum):
    TECHNICAL = "Teknik"
    TACTICAL = "Taktik"
    PHYSICAL = "Fiziksel"
    MENTAL = "Zihinsel"


class TrainingPriority(str, Enum):
    LOW = "Düşük"
    MEDIUM = "Orta"
    HIGH = "Yüksek"


class TrainingSuggestionBase(SQLModel):
    match_id: int = Field(foreign_key="matches.id")
    category: TrainingCategory
    priority: TrainingPriority
    title: str
    description: str
    target_players: Optional[List[int]] = Field(default=None, sa_column=Column(JSON))
    drill_suggestions: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    expected_improvement: Optional[str] = None
    duration_minutes: Optional[int] = None


class TrainingSuggestion(TrainingSuggestionBase, table=True):
    __tablename__ = "training_suggestions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    coach_feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TrainingSuggestionCreate(TrainingSuggestionBase):
    pass


class TrainingSuggestionRead(TrainingSuggestionBase):
    id: int
    is_completed: bool
    created_at: datetime
