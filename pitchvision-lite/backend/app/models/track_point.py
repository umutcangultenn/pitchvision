from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, JSON
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


class TrackPoint(TimestampMixin, SQLModel, table=True):
    __tablename__ = "track_point"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id", index=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", index=True)

    track_id: str = Field(max_length=64, index=True)
    frame_index: int = Field(ge=0)
    # PostgreSQL'de "timestamp" kolon adı — Python tarafında event_ts
    event_ts: datetime = Field(
        sa_column=Column("timestamp", DateTime(timezone=True), nullable=False),
        description="frame zamanı",
    )
    class_name: str = Field(max_length=64)

    bbox_json: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    pixel_x: Optional[float] = Field(default=None)
    pixel_y: Optional[float] = Field(default=None)
    field_x: Optional[float] = Field(default=None, description="metre, saha koordinatı")
    field_y: Optional[float] = Field(default=None)
    confidence: Optional[float] = Field(default=None)
