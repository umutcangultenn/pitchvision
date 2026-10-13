"""
Match Segmentation model.
Splits a match into time-based segments (e.g. 0-15, 15-30, …)
with per-segment tactical analysis results.
"""
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SegmentLabel(str, Enum):
    """Standard match segment labels."""
    MIN_0_15 = "0-15"
    MIN_15_30 = "15-30"
    MIN_30_45 = "30-45"
    HALFTIME = "halftime"
    MIN_45_60 = "45-60"
    MIN_60_75 = "60-75"
    MIN_75_90 = "75-90"
    # For halı saha / shorter matches
    MIN_0_10 = "0-10"
    MIN_10_20 = "10-20"
    MIN_20_30 = "20-30"
    HALFTIME_SHORT = "halftime-short"
    MIN_30_40 = "30-40"
    MIN_40_50 = "40-50"
    MIN_50_60 = "50-60"


class MatchSegmentBase(SQLModel):
    segment_label: str  # SegmentLabel value
    start_time: float  # seconds from match start
    end_time: float  # seconds from match start


class MatchSegment(MatchSegmentBase, table=True):
    __tablename__ = "match_segments"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id", index=True)

    # --- Flow A: Automated analysis results ---
    event_density: float = 0.0  # events per minute in this segment
    attack_tendency: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )  # {"left": 0.3, "center": 0.5, "right": 0.2}
    pressure_tendency: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )  # {"high_press": 0.4, "mid_block": 0.6}
    transition_count: int = 0
    dangerous_attacks: int = 0
    box_entries: int = 0

    # AI-generated tactical summary for this segment
    tactical_summary_ai: Optional[str] = None

    # Confidence metadata
    analysis_confidence: float = 0.0  # 0.0-1.0

    # --- Flow B: Analyst annotations (summary level) ---
    analyst_summary: Optional[str] = None  # Human-written segment summary

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MatchSegmentCreate(MatchSegmentBase):
    match_id: int


class MatchSegmentRead(MatchSegmentBase):
    id: int
    match_id: int
    event_density: float
    attack_tendency: Optional[Dict[str, Any]]
    pressure_tendency: Optional[Dict[str, Any]]
    transition_count: int
    dangerous_attacks: int
    box_entries: int
    tactical_summary_ai: Optional[str]
    analysis_confidence: float
    analyst_summary: Optional[str]
    created_at: datetime
