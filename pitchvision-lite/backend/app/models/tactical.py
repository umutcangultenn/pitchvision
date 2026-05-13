from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Enum as SAEnum, Float, JSON
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin
from app.models.enums import (
    AlertStatus,
    AlertType,
    MetricType,
    Severity,
)


class TacticalMetric(TimestampMixin, SQLModel, table=True):
    __tablename__ = "tactical_metric"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    team_id: int = Field(foreign_key="team.id", index=True)

    event_timestamp: datetime = Field(
        sa_column=Column("timestamp", DateTime(timezone=True), nullable=False),
    )
    metric_type: MetricType = Field(
        sa_column=Column(
            SAEnum(
                MetricType,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=48,
            ),
            nullable=False,
        )
    )
    value: float = Field(sa_column=Column(Float, nullable=False))
    unit: str = Field(max_length=32)
    metadata_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )


class TacticalAlert(TimestampMixin, SQLModel, table=True):
    __tablename__ = "tactical_alert"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    team_id: int = Field(foreign_key="team.id", index=True)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id", index=True)

    alert_type: AlertType = Field(
        sa_column=Column(
            SAEnum(
                AlertType,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=48,
            ),
            nullable=False,
        )
    )
    start_time: float = Field(description="video saniye")
    end_time: float = Field(description="video saniye")
    confidence: Optional[float] = Field(default=None)
    severity: Severity = Field(
        sa_column=Column(
            SAEnum(
                Severity,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=16,
            ),
            nullable=False,
        )
    )
    status: AlertStatus = Field(
        sa_column=Column(
            SAEnum(
                AlertStatus,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=32,
            ),
            nullable=False,
        )
    )
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    related_metric: Optional[str] = Field(default=None, max_length=128)
    suggested_clip_id: Optional[int] = Field(
        default=None,
        foreign_key="clip.id",
        nullable=True,
    )


class Clip(TimestampMixin, SQLModel, table=True):
    __tablename__ = "clip"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    alert_id: Optional[int] = Field(default=None, foreign_key="tactical_alert.id", index=True)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id", index=True)

    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    start_time: float = Field()
    end_time: float = Field()
    tag: Optional[str] = Field(default=None, max_length=128)
    storage_path: str = Field(max_length=1024)
    thumbnail_path: Optional[str] = Field(default=None, max_length=1024)
