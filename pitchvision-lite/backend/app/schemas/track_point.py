from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.base import ReadBase


class TrackPointCreate(BaseModel):
    match_id: int
    player_id: Optional[int] = None
    team_id: Optional[int] = None
    track_id: str = Field(max_length=64)
    frame_index: int = Field(ge=0)
    event_ts: datetime = Field(description="Video zaman damgası (DB kolonu: timestamp)")
    class_name: str = Field(max_length=64)
    bbox_json: dict[str, Any]
    pixel_x: Optional[float] = None
    pixel_y: Optional[float] = None
    field_x: Optional[float] = None
    field_y: Optional[float] = None
    confidence: Optional[float] = None


class TrackPointUpdate(BaseModel):
    match_id: Optional[int] = None
    player_id: Optional[int] = None
    team_id: Optional[int] = None
    track_id: Optional[str] = Field(default=None, max_length=64)
    frame_index: Optional[int] = Field(default=None, ge=0)
    event_ts: Optional[datetime] = None
    class_name: Optional[str] = Field(default=None, max_length=64)
    bbox_json: Optional[dict[str, Any]] = None
    pixel_x: Optional[float] = None
    pixel_y: Optional[float] = None
    field_x: Optional[float] = None
    field_y: Optional[float] = None
    confidence: Optional[float] = None


class TrackPointRead(ReadBase):
    match_id: int
    player_id: Optional[int]
    team_id: Optional[int]
    track_id: str
    frame_index: int
    event_ts: datetime
    class_name: str
    bbox_json: dict[str, Any]
    pixel_x: Optional[float]
    pixel_y: Optional[float]
    field_x: Optional[float]
    field_y: Optional[float]
    confidence: Optional[float]
