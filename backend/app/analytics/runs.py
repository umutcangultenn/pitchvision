"""
Derin koşu ve alan yaratma analizi modülü.
Oyuncuların savunma arkasına koşu fırsatlarını ve alan yaratma hareketlerini analiz eder.
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from .types import (
    TrackPoint, DepthRunCandidate, TacticalAlert, AlertType, 
    AlertSeverity, PlayerRole, TacticalConfig
)


def detect_depth_run_candidate(
    player: TrackPoint,
    defensive_line_x: float,
    ball_position: Optional[Tuple[float, float]] = None
) -> Optional[TacticalAlert]:
    """
    Tek bir oyuncu için derin koşu fırsatı tespit eder.
    
    Args:
        player: Oyuncu pozisyonu
        defensive_line_x: Rakip savunma hattının x pozisyonu
        ball_position: Top pozisyonu (x, y)
        
    Returns:
        Optional[TacticalAlert]: Tespit edilen derin koşu uyarısı veya None
    """
    if not ball_position:
        return None
    
    ball_x, ball_y = ball_position
    
    # Derin koşu kriterleri kontrol et
    criteria_met = 0
    
    # 1. Oyuncu hızı yeterli mi?
    if player.speed and player.speed > TacticalConfig.DEPTH_RUN_VELOCITY_THRESHOLD:
        criteria_met += 1
    
    # 2. X yönünde ileri hareket var mı?
    if player.vx and player.vx > 2.0:  # 2 m/s ileri hız
        criteria_met += 1
    
    # 3. Oyuncu savunma hattına yakın veya geçmiş mi?
    distance_to_line = abs(player.x - defensive_line_x)
    if player.x >= defensive_line_x - 5.0:  # 5m tolerans
        criteria_met += 1
    
    # 4. Top ile uygun mesafede mi?
    distance_to_ball = np.sqrt((player.x - ball_x)**2 + (player.y - ball_y)**2)
    if 10.0 <= distance_to_ball <= 30.0:  # Pas mesafesi
        criteria_met += 1
    
    # En az 3 kriter karşılanmalı
    if criteria_met < 3:
        return None
    
    # Güven skoru hesapla
    confidence = min(1.0, criteria_met / 4.0)
    
    # Önem seviyesi
    if criteria_met >= 4:
        severity = AlertSeverity.HIGH
    else:
        severity = AlertSeverity.MEDIUM
    
    return TacticalAlert(
        alert_type=AlertType.DEPTH_RUN_OPPORTUNITY,
        timestamp=player.timestamp,
        confidence=confidence,
        severity=severity,
        description=f"Derin koşu fırsatı - Oyuncu #{player.player_id}",
        metadata={
            "player_speed": player.speed,
            "distance_to_line": distance_to_line,
            "distance_to_ball": distance_to_ball,
            "criteria_met": criteria_met
        },
        player_ids=[player.player_id],
        team_id=player.team_id
    )


def detect_depth_run_candidate_detailed(
    player_track: List[TrackPoint],
    defensive_line_x: float,
    ball_carrier_position: Tuple[float, float],
    time_window: float = 3.0
) -> Optional[DepthRunCandidate]:
    """
    Derin koşu fırsatı adayını tespit eder.
    
    Args:
        player_track: Oyuncunun zaman içindeki pozisyon geçmişi
        defensive_line_x: Rakip savunma hattının x pozisyonu
        ball_carrier_position: Top taşıyan oyuncunun pozisyonu
        time_window: Analiz zaman penceresi (saniye)
        
    Returns:
        Optional[DepthRunCandidate]: Tespit edilen derin koşu adayı veya None
    """
    if len(player_track) < 2:
        return None
    
    # Son pozisyon ve başlangıç pozisyonu
    current_pos = player_track[-1]
    start_pos = player_track[0]
    
    # Hız hesapla
    time_diff = current_pos.timestamp - start_pos.timestamp
    if time_diff <= 0:
        return None
    
    dx = current_pos.x - start_pos.x
    dy = current_pos.y - start_pos.y
    velocity_x = dx / time_diff
    velocity_y = dy / time_diff
    
    # Derin koşu kriterleri kontrol et
    criteria_met = 0
    
    # 1. X yönünde yeterli hız (ileri doğru)
    if velocity_x > TacticalConfig.DEPTH_RUN_VELOCITY_THRESHOLD:
        criteria_met += 1
    
    # 2. Oyuncu savunma hattının gerisinde başlamış
    if start_pos.x < defensive_line_x:
        criteria_met += 1
    
    # 3. Oyuncu savunma hattına doğru veya ötesine hareket ediyor
    if current_pos.x >= defensive_line_x - 2.0:  # 2m tolerans
        criteria_met += 1
    
    # 4. Yeterli mesafe kat etmiş
    distance_covered = np.sqrt(dx**2 + dy**2)
    if distance_covered >= TacticalConfig.DEPTH_RUN_DISTANCE_THRESHOLD:
        criteria_met += 1
    
    # En az 3 kriter karşılanmalı
    if criteria_met < 3:
        return None
    
    # Pas koridoru kontrolü (basit heuristik)
    ball_x, ball_y = ball_carrier_position
    passing_lane_clear = True  # Placeholder - gerçek implementasyonda daha karmaşık
    
    # Top taşıyan ile koşu yapan arasındaki mesafe
    distance_to_ball_carrier = np.sqrt(
        (current_pos.x - ball_x)**2 + (current_pos.y - ball_y)**2
    )
    
    # Çok uzaksa pas koridoru problemli
    if distance_to_ball_carrier > 30.0:
        passing_lane_clear = False
    
    return DepthRunCandidate(
        player_id=current_pos.player_id,
        start_position=(start_pos.x, start_pos.y),
        end_position=(current_pos.x, current_pos.y),
        velocity_x=velocity_x,
        defensive_line_x=defensive_line_x,
        passing_lane_clear=passing_lane_clear,
        timestamp=current_pos.timestamp
    )


def analyze_space_creation_movement(
    player_positions: List[TrackPoint],
    teammate_positions: List[TrackPoint]
) -> Dict[str, any]:
    """
    Alan yaratma hareketlerini analiz eder.
    
    Args:
        player_positions: Analiz edilen oyuncunun pozisyonları
        teammate_positions: Takım arkadaşlarının pozisyonları
        
    Returns:
        Dict: Alan yaratma analizi
    """
    if len(player_positions) < 2 or not teammate_positions:
        return {
            "space_created": False,
            "space_value": 0.0,
            "movement_type": "unknown"
        }
    
    current_pos = player_positions[-1]
    previous_pos = player_positions[-2]
    
    # Hareket vektörü
    dx = current_pos.x - previous_pos.x
    dy = current_pos.y - previous_pos.y
    movement_distance = np.sqrt(dx**2 + dy**2)
    
    if movement_distance < 2.0:  # Minimum hareket eşiği
        return {
            "space_created": False,
            "space_value": 0.0,
            "movement_type": "static"
        }
    
    # Hareket tipini belirle
    if abs(dx) > abs(dy):
        movement_type = "horizontal" if abs(dx) > 5.0 else "diagonal"
    else:
        movement_type = "vertical" if abs(dy) > 5.0 else "diagonal"
    
    # Alan yaratma değeri hesapla
    # Oyuncunun önceki pozisyonundaki takım arkadaşı yoğunluğu
    prev_density = calculate_player_density_around_point(
        (previous_pos.x, previous_pos.y), teammate_positions, radius=10.0
    )
    
    # Oyuncunun mevcut pozisyonundaki takım arkadaşı yoğunluğu
    curr_density = calculate_player_density_around_point(
        (current_pos.x, current_pos.y), teammate_positions, radius=10.0
    )
    
    # Alan yaratma skoru (yoğunluktan uzaklaşma)
    space_value = max(0.0, prev_density - curr_density)
    space_created = space_value > 0.5  # Eşik değer
    
    return {
        "space_created": space_created,
        "space_value": space_value,
        "movement_type": movement_type,
        "movement_distance": movement_distance,
        "previous_density": prev_density,
        "current_density": curr_density
    }


def calculate_player_density_around_point(
    point: Tuple[float, float],
    players: List[TrackPoint],
    radius: float = 10.0
) -> float:
    """
    Belirli bir nokta etrafındaki oyuncu yoğunluğunu hesaplar.
    
    Args:
        point: Merkez nokta (x, y)
        players: Oyuncu pozisyonları
        radius: Analiz yarıçapı (metre)
        
    Returns:
        float: Oyuncu yoğunluğu (oyuncu/m²)
    """
    x, y = point
    players_in_radius = 0
    
    for player in players:
        distance = np.sqrt((player.x - x)**2 + (player.y - y)**2)
        if distance <= radius:
            players_in_radius += 1
    
    # Yoğunluk = oyuncu sayısı / alan
    area = np.pi * radius**2
    return players_in_radius / area


def detect_overlapping_run(
    player1_track: List[TrackPoint],
    player2_track: List[TrackPoint],
    min_overlap_distance: float = 15.0
) -> Optional[Dict[str, any]]:
    """
    İki oyuncu arasında bindirme koşusu tespit eder.
    
    Args:
        player1_track: Birinci oyuncunun pozisyon geçmişi
        player2_track: İkinci oyuncunun pozisyon geçmişi
        min_overlap_distance: Minimum bindirme mesafesi
        
    Returns:
        Optional[Dict]: Bindirme koşusu bilgileri veya None
    """
    if len(player1_track) < 2 or len(player2_track) < 2:
        return None
    
    # Son pozisyonları al
    p1_current = player1_track[-1]
    p1_previous = player1_track[-2]
    p2_current = player2_track[-1]
    p2_previous = player2_track[-2]
    
    # Hareket vektörleri
    p1_dx = p1_current.x - p1_previous.x
    p1_dy = p1_current.y - p1_previous.y
    p2_dx = p2_current.x - p2_previous.x
    p2_dy = p2_current.y - p2_previous.y
    
    # Hareket mesafeleri
    p1_distance = np.sqrt(p1_dx**2 + p1_dy**2)
    p2_distance = np.sqrt(p2_dx**2 + p2_dy**2)
    
    # Minimum hareket kontrolü
    if p1_distance < 3.0 or p2_distance < 3.0:
        return None
    
    # Oyuncular arası mesafe
    current_distance = np.sqrt(
        (p1_current.x - p2_current.x)**2 + (p1_current.y - p2_current.y)**2
    )
    
    # Bindirme koşusu kriterleri
    # 1. Oyuncular yeterince yakın
    if current_distance > min_overlap_distance:
        return None
    
    # 2. Benzer yönde hareket ediyorlar
    # Hareket vektörleri arasındaki açı
    dot_product = p1_dx * p2_dx + p1_dy * p2_dy
    magnitude_product = p1_distance * p2_distance
    
    if magnitude_product > 0:
        cos_angle = dot_product / magnitude_product
        angle_similarity = (cos_angle + 1) / 2  # 0-1 arası normalize et
    else:
        angle_similarity = 0
    
    # 3. Yeterli benzerlik
    if angle_similarity < 0.7:  # %70 benzerlik eşiği
        return None
    
    return {
        "player1_id": p1_current.player_id,
        "player2_id": p2_current.player_id,
        "overlap_distance": current_distance,
        "movement_similarity": angle_similarity,
        "timestamp": p1_current.timestamp,
        "overlap_type": "parallel_run"
    }


def analyze_wing_overload(
    attacking_players: List[TrackPoint],
    wing_side: str = "right",  # "left" or "right"
    field_width: float = TacticalConfig.FIELD_WIDTH
) -> Dict[str, any]:
    """
    Kanat yüklenmesi analiz eder.
    
    Args:
        attacking_players: Hücum eden takım oyuncuları
        wing_side: Analiz edilen kanat ("left" veya "right")
        field_width: Saha genişliği
        
    Returns:
        Dict: Kanat yüklenmesi analizi
    """
    if not attacking_players:
        return {
            "overload_detected": False,
            "player_count": 0,
            "overload_intensity": 0.0
        }
    
    # Kanat bölgesini tanımla
    if wing_side == "right":
        wing_min_y = field_width * 0.6  # Sağ kanat
        wing_max_y = field_width
    else:
        wing_min_y = 0.0  # Sol kanat
        wing_max_y = field_width * 0.4
    
    # Kanat bölgesindeki oyuncular
    wing_players = [
        p for p in attacking_players
        if wing_min_y <= p.y <= wing_max_y
    ]
    
    # Merkez bölgedeki oyuncular (karşılaştırma için)
    center_players = [
        p for p in attacking_players
        if field_width * 0.3 <= p.y <= field_width * 0.7
    ]
    
    wing_count = len(wing_players)
    center_count = len(center_players)
    total_count = len(attacking_players)
    
    # Yükleme yoğunluğu hesapla
    if total_count > 0:
        wing_ratio = wing_count / total_count
        overload_intensity = wing_ratio
    else:
        overload_intensity = 0.0
    
    # Yükleme tespit kriterleri
    overload_detected = (
        wing_count >= 3 and  # En az 3 oyuncu kanatta
        wing_count > center_count and  # Kanatta merkeze göre daha fazla oyuncu
        overload_intensity >= 0.4  # %40'tan fazla oyuncu kanatta
    )
    
    return {
        "overload_detected": overload_detected,
        "player_count": wing_count,
        "overload_intensity": overload_intensity,
        "wing_side": wing_side,
        "center_player_count": center_count,
        "wing_ratio": wing_ratio if total_count > 0 else 0.0
    }