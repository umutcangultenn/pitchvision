"""
Geçiş oyunu analizi modülü.
Hücumdan savunmaya ve savunmadan hücuma geçiş hızını ve kalitesini analiz eder.
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from .types import (
    TrackPoint, TransitionMetrics, TacticalAlert, AlertType, 
    AlertSeverity, PlayerRole, TacticalConfig
)


def calculate_transition_speed(
    start_x: float, 
    end_x: float, 
    seconds: float = TacticalConfig.TRANSITION_ANALYSIS_WINDOW
) -> float:
    """
    Geçiş oyunu hızını hesaplar.
    
    Args:
        start_x: Başlangıç x pozisyonu (metre)
        end_x: Bitiş x pozisyonu (metre)
        seconds: Geçiş süresi (saniye)
        
    Returns:
        float: Geçiş hızı (m/s)
    """
    if seconds <= 0:
        return 0.0
    
    distance = abs(end_x - start_x)
    return distance / seconds


def analyze_team_transition(
    start_positions: List[TrackPoint],
    end_positions: List[TrackPoint],
    transition_type: str = "attack"  # "attack" or "defense"
) -> TransitionMetrics:
    """
    Takım geçiş oyununu analiz eder.
    
    Args:
        start_positions: Geçiş başlangıcındaki oyuncu pozisyonları
        end_positions: Geçiş sonundaki oyuncu pozisyonları
        transition_type: Geçiş tipi ("attack" veya "defense")
        
    Returns:
        TransitionMetrics: Geçiş metrikleri
    """
    if not start_positions or not end_positions:
        return TransitionMetrics(
            start_x=0.0, end_x=0.0, duration=0.0, 
            speed=0.0, player_count=0, success=False
        )
    
    # Takım merkez pozisyonları
    start_centroid_x = np.mean([p.x for p in start_positions])
    end_centroid_x = np.mean([p.x for p in end_positions])
    
    # Zaman farkı
    duration = end_positions[0].timestamp - start_positions[0].timestamp
    
    # Geçiş hızı
    speed = calculate_transition_speed(start_centroid_x, end_centroid_x, duration)
    
    # Başarı kriteri (basit heuristik)
    if transition_type == "attack":
        # Hücum geçişi: ileri hareket ve yeterli hız
        success = (end_centroid_x > start_centroid_x and 
                  speed >= TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD)
    else:
        # Savunma geçişi: geri hareket ve kompakt durma
        success = (end_centroid_x < start_centroid_x and 
                  speed >= TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD)
    
    return TransitionMetrics(
        start_x=start_centroid_x,
        end_x=end_centroid_x,
        duration=duration,
        speed=speed,
        player_count=len(start_positions),
        success=success
    )


def detect_slow_transition_alert(
    team_players: List[TrackPoint],
    ball_position: Tuple[float, float],
    timestamp: float
) -> Optional[TacticalAlert]:
    """
    Basit yavaş geçiş oyunu uyarısı üretir (tek frame analizi).
    
    Args:
        team_players: Takım oyuncuları
        ball_position: Top pozisyonu (x, y)
        timestamp: Zaman damgası
        
    Returns:
        Optional[TacticalAlert]: Uyarı veya None
    """
    if len(team_players) < 6:  # Minimum oyuncu sayısı
        return None
    
    ball_x, ball_y = ball_position
    
    # Topa yakın oyuncuların hızlarını kontrol et
    speeds_near_ball = []
    for player in team_players:
        distance_to_ball = np.sqrt((player.x - ball_x)**2 + (player.y - ball_y)**2)
        if distance_to_ball <= 20.0 and player.speed:  # 20m içindeki oyuncular
            speeds_near_ball.append(player.speed)
    
    if not speeds_near_ball:
        return None
    
    avg_speed = np.mean(speeds_near_ball)
    
    # Yavaş geçiş kontrolü
    if avg_speed >= TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD:
        return None
    
    # Güven skoru
    confidence = 1.0 - (avg_speed / TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD)
    confidence = max(0.0, min(1.0, confidence))
    
    # Önem seviyesi
    if avg_speed < 1.5:
        severity = AlertSeverity.HIGH
    elif avg_speed < 2.5:
        severity = AlertSeverity.MEDIUM
    else:
        severity = AlertSeverity.LOW
    
    return TacticalAlert(
        alert_type=AlertType.TRANSITION_SLOW,
        timestamp=timestamp,
        confidence=confidence,
        severity=severity,
        description=f"Yavaş geçiş oyunu: {avg_speed:.1f} m/s ortalama hız",
        metadata={
            "average_speed": avg_speed,
            "players_analyzed": len(speeds_near_ball),
            "threshold": TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD
        },
        team_id=team_players[0].team_id if team_players else None
    )


def detect_slow_transition_alert_detailed(
    transition_metrics: TransitionMetrics,
    team_id: int,
    timestamp: float
) -> Optional[TacticalAlert]:
    """
    Yavaş geçiş oyunu uyarısı üretir.
    
    Args:
        transition_metrics: Geçiş metrikleri
        team_id: Takım ID'si
        timestamp: Zaman damgası
        
    Returns:
        Optional[TacticalAlert]: Uyarı veya None
    """
    if transition_metrics.speed >= TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD:
        return None
    
    # Güven skoru (ne kadar yavaş o kadar yüksek güven)
    max_expected_speed = TacticalConfig.TRANSITION_SPEED_FAST_THRESHOLD
    confidence = 1.0 - (transition_metrics.speed / max_expected_speed)
    confidence = max(0.0, min(1.0, confidence))
    
    # Önem seviyesi
    if transition_metrics.speed < 1.0:
        severity = AlertSeverity.HIGH
    elif transition_metrics.speed < 2.0:
        severity = AlertSeverity.MEDIUM
    else:
        severity = AlertSeverity.LOW
    
    return TacticalAlert(
        alert_type=AlertType.TRANSITION_SLOW,
        timestamp=timestamp,
        confidence=confidence,
        severity=severity,
        description=f"Yavaş geçiş oyunu tespit edildi. Hız: {transition_metrics.speed:.1f} m/s",
        metadata={
            "transition_speed": transition_metrics.speed,
            "transition_duration": transition_metrics.duration,
            "distance_covered": abs(transition_metrics.end_x - transition_metrics.start_x),
            "player_count": transition_metrics.player_count,
            "success": transition_metrics.success
        },
        team_id=team_id
    )


def analyze_counter_attack_opportunity(
    defending_team: List[TrackPoint],
    attacking_team: List[TrackPoint],
    ball_position: Tuple[float, float]
) -> Dict[str, any]:
    """
    Kontra atak fırsatını analiz eder.
    
    Args:
        defending_team: Savunan takım oyuncuları
        attacking_team: Hücum eden takım oyuncuları
        ball_position: Top pozisyonu (x, y)
        
    Returns:
        Dict: Kontra atak analizi
    """
    if not defending_team or not attacking_team:
        return {
            "opportunity_exists": False,
            "opportunity_score": 0.0,
            "factors": []
        }
    
    factors = []
    opportunity_score = 0.0
    
    # 1. Rakip takımın ileri pozisyonda olması
    attacking_avg_x = np.mean([p.x for p in attacking_team])
    field_length = TacticalConfig.FIELD_LENGTH
    
    if attacking_avg_x > field_length * 0.6:  # Rakip sahada %60'tan ileri
        factors.append("Rakip takım ileri pozisyonda")
        opportunity_score += 0.3
    
    # 2. Savunan takımın kompakt olması
    defending_positions = np.array([(p.x, p.y) for p in defending_team])
    defending_compactness = np.mean(np.std(defending_positions, axis=0))
    
    if defending_compactness < 15.0:  # Kompakt takım
        factors.append("Savunan takım kompakt")
        opportunity_score += 0.2
    
    # 3. Topun savunan takıma yakın olması
    ball_x, ball_y = ball_position
    defending_avg_x = np.mean([p.x for p in defending_team])
    
    if abs(ball_x - defending_avg_x) < 10.0:  # Top 10m içinde
        factors.append("Top savunan takıma yakın")
        opportunity_score += 0.2
    
    # 4. Hızlı oyuncuların varlığı
    fast_players = [
        p for p in defending_team 
        if p.speed and p.speed > 6.0  # 6 m/s üzeri hızlı oyuncu
    ]
    
    if len(fast_players) >= 2:
        factors.append("Hızlı oyuncular mevcut")
        opportunity_score += 0.3
    
    opportunity_exists = opportunity_score >= 0.5
    
    return {
        "opportunity_exists": opportunity_exists,
        "opportunity_score": opportunity_score,
        "factors": factors,
        "fast_players_count": len(fast_players),
        "attacking_team_height": attacking_avg_x / field_length
    }


def calculate_pressing_intensity(
    pressing_team: List[TrackPoint],
    ball_position: Tuple[float, float],
    time_window: float = 3.0
) -> Dict[str, float]:
    """
    Baskı yoğunluğunu hesaplar.
    
    Args:
        pressing_team: Baskı yapan takım oyuncuları
        ball_position: Top pozisyonu (x, y)
        time_window: Analiz zaman penceresi (saniye)
        
    Returns:
        Dict: Baskı yoğunluğu metrikleri
    """
    if not pressing_team:
        return {
            "intensity": 0.0,
            "players_near_ball": 0,
            "average_distance_to_ball": 0.0,
            "compactness_around_ball": 0.0
        }
    
    ball_x, ball_y = ball_position
    
    # Topa yakın oyuncular (15m içinde)
    distances_to_ball = []
    players_near_ball = 0
    
    for player in pressing_team:
        distance = np.sqrt((player.x - ball_x)**2 + (player.y - ball_y)**2)
        distances_to_ball.append(distance)
        
        if distance <= 15.0:
            players_near_ball += 1
    
    # Ortalama mesafe
    avg_distance = np.mean(distances_to_ball) if distances_to_ball else 0.0
    
    # Top etrafında kompaktlık
    near_ball_positions = [
        (p.x, p.y) for p in pressing_team 
        if np.sqrt((p.x - ball_x)**2 + (p.y - ball_y)**2) <= 20.0
    ]
    
    if len(near_ball_positions) >= 2:
        positions_array = np.array(near_ball_positions)
        compactness = np.mean(np.std(positions_array, axis=0))
    else:
        compactness = 0.0
    
    # Baskı yoğunluğu skoru (0-1)
    intensity = 0.0
    if avg_distance > 0:
        intensity += (20.0 - min(avg_distance, 20.0)) / 20.0 * 0.4  # Mesafe faktörü
    
    intensity += (players_near_ball / len(pressing_team)) * 0.4  # Oyuncu yoğunluğu
    intensity += max(0, (15.0 - compactness) / 15.0) * 0.2  # Kompaktlık faktörü
    
    return {
        "intensity": min(1.0, intensity),
        "players_near_ball": players_near_ball,
        "average_distance_to_ball": avg_distance,
        "compactness_around_ball": compactness
    }


def detect_transition_moment(
    current_frame: List[TrackPoint],
    previous_frame: List[TrackPoint],
    ball_possession_change: bool = False
) -> Optional[Dict[str, any]]:
    """
    Geçiş anını tespit eder.
    
    Args:
        current_frame: Mevcut frame'deki oyuncu pozisyonları
        previous_frame: Önceki frame'deki oyuncu pozisyonları
        ball_possession_change: Top sahipliği değişti mi?
        
    Returns:
        Optional[Dict]: Geçiş anı bilgileri veya None
    """
    if not current_frame or not previous_frame:
        return None
    
    # Takım hızlarını hesapla
    team_speeds = {}
    
    for curr_player in current_frame:
        prev_player = next(
            (p for p in previous_frame if p.player_id == curr_player.player_id), 
            None
        )
        
        if prev_player:
            time_diff = curr_player.timestamp - prev_player.timestamp
            if time_diff > 0:
                speed = np.sqrt(
                    (curr_player.x - prev_player.x)**2 + 
                    (curr_player.y - prev_player.y)**2
                ) / time_diff
                
                team_id = curr_player.team_id
                if team_id not in team_speeds:
                    team_speeds[team_id] = []
                team_speeds[team_id].append(speed)
    
    # Ortalama takım hızları
    avg_team_speeds = {
        team_id: np.mean(speeds) 
        for team_id, speeds in team_speeds.items()
    }
    
    # Geçiş tespit kriterleri
    transition_detected = False
    transition_type = None
    
    # 1. Top sahipliği değişimi
    if ball_possession_change:
        transition_detected = True
        transition_type = "possession_change"
    
    # 2. Ani hız artışı
    elif any(speed > 4.0 for speed in avg_team_speeds.values()):
        transition_detected = True
        transition_type = "speed_increase"
    
    if not transition_detected:
        return None
    
    return {
        "transition_type": transition_type,
        "timestamp": current_frame[0].timestamp,
        "team_speeds": avg_team_speeds,
        "ball_possession_change": ball_possession_change
    }