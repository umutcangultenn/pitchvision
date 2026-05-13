from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.enums import VideoAssetStatus
from app.schemas.base import ReadBase


class VideoAssetCreate(BaseModel):
    match_id: int
    file_name: str = Field(max_length=512)
    storage_path: str = Field(max_length=1024)
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    status: VideoAssetStatus


class VideoAssetUpdate(BaseModel):
    match_id: Optional[int] = None
    file_name: Optional[str] = Field(default=None, max_length=512)
    storage_path: Optional[str] = Field(default=None, max_length=1024)
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    status: Optional[VideoAssetStatus] = None


class VideoAssetRead(ReadBase):
    match_id: int
    file_name: str
    storage_path: str
    duration_seconds: Optional[float]
    width: Optional[int]
    height: Optional[int]
    fps: Optional[float]
    status: VideoAssetStatus


class FieldCalibrationCreate(BaseModel):
    match_id: int
    frame_time: float
    points_json: dict[str, Any]
    homography_json: dict[str, Any] = Field(default_factory=dict)
    average_error_m: Optional[float] = None
    quality: Optional[float] = None


class FieldCalibrationUpdate(BaseModel):
    match_id: Optional[int] = None
    frame_time: Optional[float] = None
    points_json: Optional[dict[str, Any]] = None
    homography_json: Optional[dict[str, Any]] = None
    average_error_m: Optional[float] = None
    quality: Optional[float] = None


class FieldCalibrationRead(ReadBase):
    match_id: int
    frame_time: float
    points_json: dict[str, Any]
    homography_json: dict[str, Any]
    average_error_m: Optional[float]
    quality: Optional[float]
