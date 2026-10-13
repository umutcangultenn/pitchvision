"""
Analyst Event model.
Human analyst manually tagged events (Flow B).
Supports all 12 event tags from the specification.
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventTag(str, Enum):
    """All supported manual event tags for the analyst workflow."""
    SHOT = "shot"
    GOAL = "goal"
    POSSESSION_LOSS = "possession_loss"
    POSSESSION_REGAIN = "possession_regain"
    PRESSING_MOMENT = "pressing_moment"
    TRANSITION = "transition"
    DANGEROUS_ATTACK = "dangerous_attack"
    BUILDUP_ISSUE = "buildup_issue"
    COMPACTNESS_ISSUE = "compactness_issue"
    COUNTER_ATTACK = "counter_attack"
    WING_OVERLOAD = "wing_overload"
    DEFENSIVE_BREAKDOWN = "defensive_breakdown"


class AnalystConfidence(str, Enum):
    """How confident the analyst is in their observation."""
    CERTAIN = "certain"
    PROBABLE = "probable"
    UNCERTAIN = "uncertain"


class ValidationStatus(str, Enum):
    """When an analyst event validates/rejects an engine event."""
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    MODIFIED = "modified"


class AnalystEventBase(SQLModel):
    tag: str  # EventTag value
    timestamp_seconds: float  # seconds from match start
    notes: Optional[str] = None
    confidence: str = "probable"  # AnalystConfidence value


class AnalystEvent(AnalystEventBase, table=True):
    __tablename__ = "analyst_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id", index=True)
    segment_id: Optional[int] = Field(
        default=None, foreign_key="match_segments.id", index=True
    )
    analyst_id: int = Field(foreign_key="users.id", index=True)

    # --- Cross-reference with engine events ---
    validates_engine_event_id: Optional[int] = Field(
        default=None, foreign_key="engine_events.id"
    )
    validation_status: Optional[str] = None  # ValidationStatus value

    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AnalystEventCreate(AnalystEventBase):
    match_id: int
    segment_id: Optional[int] = None
    validates_engine_event_id: Optional[int] = None
    validation_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalystEventRead(AnalystEventBase):
    id: int
    match_id: int
    segment_id: Optional[int]
    analyst_id: int
    validates_engine_event_id: Optional[int]
    validation_status: Optional[str]
    created_at: datetime
    updated_at: datetime


class AnalystEventUpdate(SQLModel):
    tag: Optional[str] = None
    timestamp_seconds: Optional[float] = None
    notes: Optional[str] = None
    confidence: Optional[str] = None
    validation_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
