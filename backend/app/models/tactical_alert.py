from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCategory(str, Enum):
    DEFENSIVE = "Savunma"
    OFFENSIVE = "Hücum"
    POSSESSION = "Top Hakimiyeti"
    TRANSITION = "Geçiş Oyunu"
    SET_PIECE = "Duran Top"
    PHYSICAL = "Fiziksel"


class TacticalAlertBase(SQLModel):
    category: AlertCategory
    severity: AlertSeverity
    title: str
    description: str
    timestamp_seconds: Optional[float] = None
    video_clip_url: Optional[str] = None
    alert_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class TacticalAlert(TacticalAlertBase, table=True):
    __tablename__ = "tactical_alerts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id")
    is_reviewed: bool = False
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    coach_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    match: "Match" = Relationship(back_populates="tactical_alerts")


class TacticalAlertCreate(TacticalAlertBase):
    match_id: int


class TacticalAlertRead(TacticalAlertBase):
    id: int
    match_id: int
    is_reviewed: bool
    created_at: datetime
    disclaimer: str = "Bu uyarı otomatik analiz adayıdır. Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır."
