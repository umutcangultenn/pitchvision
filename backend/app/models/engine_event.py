"""
Engine Event model.
Represents automatically detected tactical moments (Flow A).
All detections are suggestions — never treated as absolute truth.
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class EngineEventType(str, Enum):
    """Types of events the engine can detect."""
    DANGEROUS_ATTACK = "dangerous_attack"
    RAPID_TRANSITION = "rapid_transition"
    BOX_ENTRY = "box_entry"
    PRESSURE_MOMENT = "pressure_moment"
    DEFENSIVE_CLUSTER = "defensive_cluster"
    ATTACKING_OVERLOAD = "attacking_overload"
    TRANSITION_BURST = "transition_burst"
    COUNTER_ATTACK = "counter_attack"
    WING_OVERLOAD = "wing_overload"
    POSSESSION_LOSS = "possession_loss"
    POSSESSION_REGAIN = "possession_regain"
    COMPACTNESS_ISSUE = "compactness_issue"
    DEFENSIVE_BREAKDOWN = "defensive_breakdown"
    BUILDUP_ISSUE = "buildup_issue"
    SHOT = "shot"
    GOAL = "goal"


class AnalystVerdict(str, Enum):
    """Analyst validation states for engine events."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    MODIFIED = "modified"


class EngineEventBase(SQLModel):
    event_type: str  # EngineEventType value
    timestamp_seconds: float  # seconds from match start
    duration_seconds: Optional[float] = None
    confidence: float = 0.0  # 0.0-1.0 — engine NEVER claims > 0.85
    description: str = ""  # AI-generated, uses suggestion language


class EngineEvent(EngineEventBase, table=True):
    __tablename__ = "engine_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id", index=True)
    segment_id: Optional[int] = Field(
        default=None, foreign_key="match_segments.id", index=True
    )

    # Evidence: what data triggered this detection
    evidence: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )

    # --- Analyst validation (Flow B feedback on Flow A) ---
    analyst_reviewed: bool = False
    analyst_verdict: Optional[str] = None  # AnalystVerdict value
    analyst_notes: Optional[str] = None
    reviewed_by: Optional[int] = Field(
        default=None, foreign_key="users.id"
    )
    reviewed_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class EngineEventCreate(EngineEventBase):
    match_id: int
    segment_id: Optional[int] = None
    evidence: Optional[Dict[str, Any]] = None


class EngineEventRead(EngineEventBase):
    id: int
    match_id: int
    segment_id: Optional[int]
    evidence: Optional[Dict[str, Any]]
    analyst_reviewed: bool
    analyst_verdict: Optional[str]
    analyst_notes: Optional[str]
    created_at: datetime


class EngineEventReview(SQLModel):
    """Schema for analyst reviewing an engine event."""
    verdict: str  # AnalystVerdict value
    notes: Optional[str] = None
