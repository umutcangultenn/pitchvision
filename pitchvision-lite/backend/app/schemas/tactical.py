from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.enums import (
    AlertStatus,
    AlertType,
    MetricType,
    Severity,
)
from app.schemas.base import ReadBase


class TacticalMetricCreate(BaseModel):
    match_id: int
    team_id: int
    event_timestamp: datetime
    metric_type: MetricType
    value: float
    unit: str = Field(max_length=32)
    metadata_json: Optional[dict[str, Any]] = None


class TacticalMetricUpdate(BaseModel):
    match_id: Optional[int] = None
    team_id: Optional[int] = None
    event_timestamp: Optional[datetime] = None
    metric_type: Optional[MetricType] = None
    value: Optional[float] = None
    unit: Optional[str] = Field(default=None, max_length=32)
    metadata_json: Optional[dict[str, Any]] = None


class TacticalMetricRead(ReadBase):
    match_id: int
    team_id: int
    event_timestamp: datetime
    metric_type: MetricType
    value: float
    unit: str
    metadata_json: Optional[dict[str, Any]]


class TacticalAlertCreate(BaseModel):
    match_id: int
    team_id: int
    player_id: Optional[int] = None
    alert_type: AlertType
    start_time: float
    end_time: float
    confidence: Optional[float] = None
    severity: Severity
    status: AlertStatus
    title: str = Field(max_length=255)
    description: Optional[str] = None
    related_metric: Optional[str] = Field(default=None, max_length=128)
    suggested_clip_id: Optional[int] = None


class TacticalAlertUpdate(BaseModel):
    match_id: Optional[int] = None
    team_id: Optional[int] = None
    player_id: Optional[int] = None
    alert_type: Optional[AlertType] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    confidence: Optional[float] = None
    severity: Optional[Severity] = None
    status: Optional[AlertStatus] = None
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    related_metric: Optional[str] = Field(default=None, max_length=128)
    suggested_clip_id: Optional[int] = None


class TacticalAlertRead(ReadBase):
    match_id: int
    team_id: int
    player_id: Optional[int]
    alert_type: AlertType
    start_time: float
    end_time: float
    confidence: Optional[float]
    severity: Severity
    status: AlertStatus
    title: str
    description: Optional[str]
    related_metric: Optional[str]
    suggested_clip_id: Optional[int]


class ClipCreate(BaseModel):
    match_id: int
    alert_id: Optional[int] = None
    player_id: Optional[int] = None
    title: str = Field(max_length=255)
    description: Optional[str] = None
    start_time: float
    end_time: float
    tag: Optional[str] = Field(default=None, max_length=128)
    storage_path: str = Field(max_length=1024)
    thumbnail_path: Optional[str] = Field(default=None, max_length=1024)


class ClipUpdate(BaseModel):
    match_id: Optional[int] = None
    alert_id: Optional[int] = None
    player_id: Optional[int] = None
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    tag: Optional[str] = Field(default=None, max_length=128)
    storage_path: Optional[str] = Field(default=None, max_length=1024)
    thumbnail_path: Optional[str] = Field(default=None, max_length=1024)


class ClipRead(ReadBase):
    match_id: int
    alert_id: Optional[int]
    player_id: Optional[int]
    title: str
    description: Optional[str]
    start_time: float
    end_time: float
    tag: Optional[str]
    storage_path: str
    thumbnail_path: Optional[str]
