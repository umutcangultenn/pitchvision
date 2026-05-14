from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    COACH = "coach"
    SCOUT = "scout"
    ANALYST = "analyst"
    VIEWER = "viewer"


class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VideoSource(str, Enum):
    FILE_UPLOAD = "file_upload"
    URL_STREAM = "url_stream"
    YOUTUBE = "youtube"
    OTHER = "other"


class VideoAssetStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class AlertType(str, Enum):
    PRESSING = "pressing"
    COUNTER_ATTACK = "counter_attack"
    TRANSITION = "transition"
    SET_PIECE = "set_piece"
    WING_OVERLOAD = "wing_overload"
    HALF_SPACE = "half_space"
    DUEL = "duel"
    LINE_BREAKING_PASS = "line_breaking_pass"
    # tactical analytics engine
    DEFENSIVE_LINE_BREAK = "defensive_line_break"
    BLOCK_GAP_WIDE = "block_gap_wide"
    DEPTH_RUN_OPPORTUNITY = "depth_run_opportunity"
    POOR_TRANSITION_DEFENSE = "poor_transition_defense"
    COMPACTNESS_LOST = "compactness_lost"
    LACK_OF_SUPPORT_RUN = "lack_of_support_run"
    OTHER = "other"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportType(str, Enum):
    MATCH_SUMMARY = "match_summary"
    PLAYER_DEVELOPMENT = "player_development"
    SCOUTING = "scouting"
    TACTICAL = "tactical"
    TRAINING = "training"


class MetricType(str, Enum):
    PASS_NETWORK = "pass_network"
    PPDA = "ppda"
    PROGRESSIVE_PASSES = "progressive_passes"
    XG = "xg"
    FIELD_TILT = "field_tilt"
    CUSTOM = "custom"


class ProblemType(str, Enum):
    TECHNICAL = "technical"
    TACTICAL = "tactical"
    PHYSICAL = "physical"
    DECISION = "decision"


class PitchSize(str, Enum):
    FULL = "full"
    HALF = "half"
    SMALL_SIDED = "small_sided"


class DrillDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
