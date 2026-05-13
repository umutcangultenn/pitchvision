from typing import Any, Optional

from sqlalchemy import Column, Enum as SAEnum, JSON
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin
from app.models.enums import VideoAssetStatus


class VideoAsset(TimestampMixin, SQLModel, table=True):
    __tablename__ = "video_asset"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)

    file_name: str = Field(max_length=512)
    storage_path: str = Field(max_length=1024)
    duration_seconds: Optional[float] = Field(default=None)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    fps: Optional[float] = Field(default=None)
    status: VideoAssetStatus = Field(
        sa_column=Column(
            SAEnum(
                VideoAssetStatus,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=32,
            ),
            nullable=False,
        )
    )


class FieldCalibration(TimestampMixin, SQLModel, table=True):
    __tablename__ = "field_calibration"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)

    frame_time: float = Field(description="saniye")
    points_json: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    homography_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    average_error_m: Optional[float] = Field(default=None)
    quality: Optional[float] = Field(default=None)
