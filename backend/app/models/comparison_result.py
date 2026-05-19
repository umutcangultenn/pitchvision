"""
Comparison Result model.
Stores the outcome of AI vs Human Analyst comparison for a match.
Core feature for analyst development and AI reliability tracking.
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime


class ComparisonResultBase(SQLModel):
    total_engine_events: int = 0
    total_analyst_events: int = 0
    overlapping_events: int = 0
    engine_only_events: int = 0  # Detected by AI, missed by analyst
    analyst_only_events: int = 0  # Detected by analyst, missed by AI
    agreement_ratio: float = 0.0  # 0.0-1.0


class ComparisonResult(ComparisonResultBase, table=True):
    __tablename__ = "comparison_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id", index=True)

    # Detailed breakdown by event type
    breakdown_by_type: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    # Example:
    # {
    #   "dangerous_attack": {"engine": 5, "analyst": 3, "overlap": 2},
    #   "transition": {"engine": 8, "analyst": 6, "overlap": 4},
    #   ...
    # }

    # Event-level matching details
    matched_pairs: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    # List of {engine_event_id, analyst_event_id, time_diff, type_match}

    # AI-generated comparison summary
    comparison_summary: Optional[str] = None

    # Configuration used for comparison
    time_window_seconds: float = 10.0  # Matching tolerance

    created_at: datetime = Field(default_factory=datetime.utcnow)


class ComparisonResultRead(ComparisonResultBase):
    id: int
    match_id: int
    breakdown_by_type: Optional[Dict[str, Any]]
    comparison_summary: Optional[str]
    time_window_seconds: float
    created_at: datetime


class ComparisonDetailRead(ComparisonResultRead):
    """Extended read with matched pair details."""
    matched_pairs: Optional[Dict[str, Any]]
