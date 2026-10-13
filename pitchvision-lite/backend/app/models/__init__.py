"""Veritabanı modelleri — Alembic autogenerate için tüm tablolar burada import edilir."""

from app.models.drill import DrillRecommendation
from app.models.enums import (
    AlertStatus,
    AlertType,
    DrillDifficulty,
    MatchStatus,
    MetricType,
    PitchSize,
    ProblemType,
    ReportType,
    Severity,
    UserRole,
    VideoAssetStatus,
    VideoSource,
)
from app.models.match import Match
from app.models.organization import Organization
from app.models.performance import PlayerMatchPerformance, ScoutNote
from app.models.player import Player
from app.models.privacy import AuditLog, ParentalConsent  # noqa: F401
from app.models.report import Report
from app.models.tactical import Clip, TacticalAlert, TacticalMetric
from app.models.team import Team
from app.models.track_point import TrackPoint
from app.models.user import User
from app.models.video import FieldCalibration, VideoAsset

__all__ = [
    "AlertStatus",
    "AlertType",
    "DrillDifficulty",
    "DrillRecommendation",
    "Clip",
    "FieldCalibration",
    "Match",
    "MatchStatus",
    "MetricType",
    "Organization",
    "PitchSize",
    "Player",
    "PlayerMatchPerformance",
    "ProblemType",
    "Report",
    "ReportType",
    "ScoutNote",
    "Severity",
    "TacticalAlert",
    "TacticalMetric",
    "Team",
    "TrackPoint",
    "User",
    "UserRole",
    "VideoAsset",
    "VideoAssetStatus",
    "VideoSource",
]
