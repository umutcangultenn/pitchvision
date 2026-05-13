"""
Tactical analytics için veri tipleri ve yapıları.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import numpy as np


class PlayerRole(Enum):
    """Oyuncu pozisyon rolleri."""
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"


class AlertSeverity(Enum):
    """Uyarı önem seviyeleri."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Taktiksel uyarı tipleri."""
    DEFENSIVE_LINE_BREAK = "defensive_line_break"
    BLOCK_GAP_WIDE = "block_gap_wide"
    DEPTH_RUN_OPPORTUNITY = "depth_run_opportunity"
    TRANSITION_SLOW = "transition_slow"
    COMPACTNESS_LOST = "compactness_lost"
    OFFSIDE_TRAP_FAILED = "offside_trap_failed"


@dataclass
class TrackPoint:
    """Oyuncu tracking verisi için temel veri yapısı."""
    player_id: int
    team_id: int
    role: PlayerRole
    timestamp: float  # seconds
    x: float  # meters, field coordinates
    y: float  # meters, field coordinates
    speed: Optional[float] = None  # m/s
    vx: Optional[float] = None  # velocity x component m/s
    vy: Optional[float] = None  # velocity y component m/s


@dataclass
class TeamShape:
    """Takım şekli metrikleri."""
    team_length: float  # meters
    team_width: float  # meters
    centroid_x: float  # meters
    centroid_y: float  # meters
    compactness: float  # meters, average distance from centroid


@dataclass
class BlockGaps:
    """Bloklar arası mesafeler."""
    defensive_midfield_gap: float  # meters
    midfield_forward_gap: float  # meters


@dataclass
class DefensiveLineError:
    """Savunma hattı hata analizi."""
    player_id: int
    line_x: float  # meters, average defensive line position
    line_error: float  # meters, deviation from line
    is_offside_trap: bool = False


@dataclass
class TacticalAlert:
    """Taktiksel uyarı."""
    alert_type: AlertType
    timestamp: float  # seconds
    confidence: float  # 0.0 to 1.0
    severity: AlertSeverity
    description: str
    metadata: Dict[str, Any]  # Additional context data
    player_ids: Optional[List[int]] = None
    team_id: Optional[int] = None


@dataclass
class TransitionMetrics:
    """Geçiş oyunu metrikleri."""
    start_x: float
    end_x: float
    duration: float  # seconds
    speed: float  # m/s
    player_count: int
    success: bool


@dataclass
class DepthRunCandidate:
    """Derin koşu fırsatı adayı."""
    player_id: int
    start_position: tuple  # (x, y)
    end_position: tuple  # (x, y)
    velocity_x: float  # m/s
    defensive_line_x: float  # meters
    passing_lane_clear: bool
    timestamp: float  # seconds


# Konfigürasyon sabitleri
class TacticalConfig:
    """Taktiksel analiz konfigürasyonu."""
    
    # Savunma hattı eşikleri
    DEFENSIVE_LINE_BREAK_THRESHOLD = 4.0  # meters
    DEFENSIVE_LINE_BREAK_HIGH_THRESHOLD = 6.0  # meters
    
    # Blok mesafe eşikleri
    BLOCK_GAP_WARNING_THRESHOLD = 25.0  # meters
    BLOCK_GAP_CRITICAL_THRESHOLD = 35.0  # meters
    
    # Geçiş hızı eşikleri
    TRANSITION_SPEED_SLOW_THRESHOLD = 3.0  # m/s
    TRANSITION_SPEED_FAST_THRESHOLD = 6.0  # m/s
    
    # Derin koşu eşikleri
    DEPTH_RUN_VELOCITY_THRESHOLD = 4.0  # m/s
    DEPTH_RUN_DISTANCE_THRESHOLD = 10.0  # meters
    
    # Kompaktlık eşikleri
    COMPACTNESS_WARNING_THRESHOLD = 20.0  # meters
    COMPACTNESS_CRITICAL_THRESHOLD = 30.0  # meters
    
    # Zaman pencereleri
    TRANSITION_ANALYSIS_WINDOW = 5.0  # seconds
    DEFENSIVE_LINE_ANALYSIS_WINDOW = 3.0  # seconds
    
    # Saha boyutları (standart)
    FIELD_LENGTH = 105.0  # meters
    FIELD_WIDTH = 68.0  # meters