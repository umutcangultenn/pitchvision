from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    QUEUED = "queued"
    DETECTING = "detecting"
    TRACKING = "tracking"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisBase(SQLModel):
    fps: float = 25.0
    total_frames: int = 0
    processed_frames: int = 0
    detection_confidence: float = 0.5
    tracking_method: str = "mock"  # mock, yolo, deepsort


class Analysis(AnalysisBase, table=True):
    __tablename__ = "analyses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id", unique=True)
    status: AnalysisStatus = AnalysisStatus.QUEUED
    
    # Tracking data
    tracking_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Tactical metrics
    possession_home: Optional[float] = None
    possession_away: Optional[float] = None
    passes_completed_home: Optional[int] = None
    passes_completed_away: Optional[int] = None
    shots_home: Optional[int] = None
    shots_away: Optional[int] = None
    distance_covered: Optional[Dict[str, float]] = Field(default=None, sa_column=Column(JSON))
    heatmap_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Processing info
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    match: "Match" = Relationship(back_populates="analysis")


class AnalysisCreate(AnalysisBase):
    match_id: int


class AnalysisRead(AnalysisBase):
    id: int
    match_id: int
    status: AnalysisStatus
    possession_home: Optional[float]
    possession_away: Optional[float]
    passes_completed_home: Optional[int]
    passes_completed_away: Optional[int]
    shots_home: Optional[int]
    shots_away: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    processing_time_seconds: Optional[float]
    progress_percentage: Optional[float] = 0.0
