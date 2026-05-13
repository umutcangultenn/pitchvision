"""API için saf Pydantic şemaları (SQLModel taban şemalarından ayrı)."""

from app.schemas.drill import (
    DrillRecommendationCreate,
    DrillRecommendationRead,
    DrillRecommendationUpdate,
)
from app.schemas.match import MatchCreate, MatchRead, MatchUpdate
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
)
from app.schemas.performance import (
    PlayerMatchPerformanceCreate,
    PlayerMatchPerformanceRead,
    PlayerMatchPerformanceUpdate,
    ScoutNoteCreate,
    ScoutNoteRead,
    ScoutNoteUpdate,
)
from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate
from app.schemas.report import ReportCreate, ReportRead, ReportUpdate
from app.schemas.tactical import (
    ClipCreate,
    ClipRead,
    ClipUpdate,
    TacticalAlertCreate,
    TacticalAlertRead,
    TacticalAlertUpdate,
    TacticalMetricCreate,
    TacticalMetricRead,
    TacticalMetricUpdate,
)
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate
from app.schemas.track_point import (
    TrackPointCreate,
    TrackPointRead,
    TrackPointUpdate,
)
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common_api import DictResponse, MessageResponse
from app.schemas.player_extras import PlayerClipsRead, PlayerPassportRead, PlayerPerformancesRead
from app.schemas.settings import AppSettingsRead, AppSettingsUpdate
from app.schemas.video import (
    FieldCalibrationCreate,
    FieldCalibrationRead,
    FieldCalibrationUpdate,
    VideoAssetCreate,
    VideoAssetRead,
    VideoAssetUpdate,
)

__all__ = [
    "ClipCreate",
    "ClipRead",
    "ClipUpdate",
    "DictResponse",
    "DrillRecommendationCreate",
    "DrillRecommendationRead",
    "DrillRecommendationUpdate",
    "FieldCalibrationCreate",
    "FieldCalibrationRead",
    "FieldCalibrationUpdate",
    "MatchCreate",
    "MatchRead",
    "MatchUpdate",
    "OrganizationCreate",
    "OrganizationRead",
    "OrganizationUpdate",
    "PlayerCreate",
    "PlayerClipsRead",
    "PlayerMatchPerformanceCreate",
    "PlayerMatchPerformanceRead",
    "PlayerMatchPerformanceUpdate",
    "PlayerRead",
    "PlayerPassportRead",
    "PlayerPerformancesRead",
    "PlayerUpdate",
    "LoginRequest",
    "RegisterRequest",
    "ReportCreate",
    "ReportRead",
    "ReportUpdate",
    "ScoutNoteCreate",
    "ScoutNoteRead",
    "ScoutNoteUpdate",
    "TacticalAlertCreate",
    "TacticalAlertRead",
    "TacticalAlertUpdate",
    "TacticalMetricCreate",
    "TacticalMetricRead",
    "TacticalMetricUpdate",
    "TeamCreate",
    "TeamRead",
    "TeamUpdate",
    "TrackPointCreate",
    "TrackPointRead",
    "TrackPointUpdate",
    "MessageResponse",
    "AppSettingsRead",
    "AppSettingsUpdate",
    "TokenResponse",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "VideoAssetCreate",
    "VideoAssetRead",
    "VideoAssetUpdate",
]
