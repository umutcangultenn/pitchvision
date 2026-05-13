from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime


class PlayerMetricBase(SQLModel):
    match_id: int = Field(foreign_key="matches.id")
    
    # Performance metrics
    minutes_played: Optional[int] = None
    distance_covered_km: Optional[float] = None
    sprint_count: Optional[int] = None
    max_speed_kmh: Optional[float] = None
    
    # Technical metrics
    passes_attempted: Optional[int] = None
    passes_completed: Optional[int] = None
    pass_accuracy: Optional[float] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    dribbles_attempted: Optional[int] = None
    dribbles_successful: Optional[int] = None
    
    # Defensive metrics
    tackles: Optional[int] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    
    # Positional data
    heatmap_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    position_zones: Optional[Dict[str, float]] = Field(default=None, sa_column=Column(JSON))
    
    # Development score (0-100)
    technical_score: Optional[float] = None
    tactical_score: Optional[float] = None
    physical_score: Optional[float] = None
    mental_score: Optional[float] = None
    overall_score: Optional[float] = None


class PlayerMetric(PlayerMetricBase, table=True):
    __tablename__ = "player_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="players.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    player: "Player" = Relationship(back_populates="metrics")


class PlayerMetricCreate(PlayerMetricBase):
    player_id: int


class PlayerMetricRead(PlayerMetricBase):
    id: int
    player_id: int
    created_at: datetime
