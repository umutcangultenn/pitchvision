from datetime import date
from typing import Any, Optional

from pydantic import BaseModel

from app.schemas.performance import PlayerMatchPerformanceRead
from app.schemas.tactical import ClipRead


class PlayerPassportRead(BaseModel):
    """Kapsamlı oyuncu pasaportu verileri"""
    player_id: int
    first_name: str
    last_name: str
    birth_date: date
    position: str
    dominant_foot: str
    height_cm: Optional[float]
    weight_kg: Optional[float]
    photo_url: Optional[str]
    team_name: Optional[str]
    
    # Skorlar
    technical_score: Optional[float]
    tactical_score: Optional[float]
    physical_score: Optional[float]
    decision_score: Optional[float]
    development_velocity: Optional[float]
    
    # İstatistikler
    matches_played: int
    average_max_speed: float
    average_speed: float
    total_positive_actions: int
    total_alerts_involved: int
    
    # Trendler (8 hafta)
    trend_data: list[dict[str, Any]]
    
    # Taktiksel profil
    tactical_profile: dict[str, Any]


class PlayerPerformancesRead(BaseModel):
    items: list[PlayerMatchPerformanceRead]


class PlayerClipsRead(BaseModel):
    items: list[ClipRead]
