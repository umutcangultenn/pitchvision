from .user import User, UserCreate, UserRead, UserUpdate
from .team import Team, TeamCreate, TeamRead, TeamUpdate
from .player import Player, PlayerCreate, PlayerRead, PlayerUpdate
from .match import Match, MatchCreate, MatchRead, MatchUpdate, MatchStatus
from .analysis import Analysis, AnalysisCreate, AnalysisRead, AnalysisStatus
from .tactical_alert import TacticalAlert, TacticalAlertCreate, TacticalAlertRead, AlertSeverity
from .player_metric import PlayerMetric, PlayerMetricCreate, PlayerMetricRead
from .training_suggestion import TrainingSuggestion, TrainingSuggestionCreate, TrainingSuggestionRead
from .match_segment import MatchSegment, MatchSegmentCreate, MatchSegmentRead, SegmentLabel
from .engine_event import EngineEvent, EngineEventCreate, EngineEventRead, EngineEventReview, EngineEventType, AnalystVerdict
from .analyst_event import AnalystEvent, AnalystEventCreate, AnalystEventRead, AnalystEventUpdate, EventTag, AnalystConfidence, ValidationStatus
from .comparison_result import ComparisonResult, ComparisonResultRead, ComparisonDetailRead

__all__ = [
    "User", "UserCreate", "UserRead", "UserUpdate",
    "Team", "TeamCreate", "TeamRead", "TeamUpdate",
    "Player", "PlayerCreate", "PlayerRead", "PlayerUpdate",
    "Match", "MatchCreate", "MatchRead", "MatchUpdate", "MatchStatus",
    "Analysis", "AnalysisCreate", "AnalysisRead", "AnalysisStatus",
    "TacticalAlert", "TacticalAlertCreate", "TacticalAlertRead", "AlertSeverity",
    "PlayerMetric", "PlayerMetricCreate", "PlayerMetricRead",
    "TrainingSuggestion", "TrainingSuggestionCreate", "TrainingSuggestionRead",
    # --- Tactical Engine Upgrade models ---
    "MatchSegment", "MatchSegmentCreate", "MatchSegmentRead", "SegmentLabel",
    "EngineEvent", "EngineEventCreate", "EngineEventRead", "EngineEventReview",
    "EngineEventType", "AnalystVerdict",
    "AnalystEvent", "AnalystEventCreate", "AnalystEventRead", "AnalystEventUpdate",
    "EventTag", "AnalystConfidence", "ValidationStatus",
    "ComparisonResult", "ComparisonResultRead", "ComparisonDetailRead",
]
