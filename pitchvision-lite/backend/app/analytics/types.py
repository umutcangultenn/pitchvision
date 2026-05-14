from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlayerRole(str, Enum):
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"


class AlertType(str, Enum):
    DEFENSIVE_LINE_BREAK = "defensive_line_break"
    BLOCK_GAP_WIDE = "block_gap_wide"
    COMPACTNESS_LOST = "compactness_lost"
    TRANSITION_SLOW = "transition_slow"
    OFFSIDE_TRAP_FAILED = "offside_trap_failed"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TrackPoint:
    player_id: int
    team_id: int
    role: PlayerRole
    timestamp: float
    x: float
    y: float
    speed: float | None = None
    vx: float | None = None
    vy: float | None = None


@dataclass
class TacticalConfig:
    FIELD_LENGTH: float = 105.0
    FIELD_WIDTH: float = 68.0
    BLOCK_GAP_WARNING_THRESHOLD: float = 15.0
    BLOCK_GAP_CRITICAL_THRESHOLD: float = 25.0
    COMPACTNESS_WARNING_THRESHOLD: float = 20.0
    COMPACTNESS_CRITICAL_THRESHOLD: float = 30.0
    TRANSITION_SPEED_SLOW_THRESHOLD: float = 4.0


@dataclass
class TeamShape:
    team_length: float
    team_width: float
    centroid_x: float
    centroid_y: float
    compactness: float


@dataclass
class BlockGaps:
    defensive_midfield_gap: float
    midfield_forward_gap: float


@dataclass
class DefensiveLineError:
    line_x: float
    line_error: float
    is_offside_trap: bool = False


@dataclass
class TransitionMetrics:
    start_x: float
    end_x: float
    duration: float
    speed: float
    player_count: int
    success: bool = False


@dataclass
class TacticalAlert:
    alert_type: AlertType
    timestamp: float
    confidence: float
    severity: AlertSeverity
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)
    team_id: int = 1
