"""
Savunma hattı analizi modülü.
Savunma hattının düzgünlüğünü ve ofsayt tuzağı etkinliğini analiz eder.
"""
import numpy as np
from typing import List, Dict, Optional
from .types import (
    TrackPoint, DefensiveLineError, TacticalAlert, AlertType, 
    AlertSeverity, PlayerRole, TacticalConfig
)


def calculate_defensive_line_errors(defenders: List[TrackPoint]) -> List[DefensiveLineError]:
    """
    Savunma hattındaki oyuncuların hat düzgünlüğünden sapmalarını hesaplar.
    
    Args:
        defenders: Savunma oyuncularının tracking verileri
        
    Returns:
        List[DefensiveLineError]: Her savunma oyuncusu için hat hatası
    """
    if len(defenders) < 2:
        return []
    
    # Savunma hattının ortalama x pozisyonu
    x_positions = [d.x for d in defenders]
    line_x = np.mean(x_positions)
    
    errors = []
    for defender in defenders:
        line_error = abs(defender.x - line_x)
        
        errors.append(DefensiveLineError(
            player_id=defender.player_id,
            line_x=line_x,
            line_error=line_error,
            is_offside_trap=defender.x > line_x  # Hat önünde ise ofsayt tuzağı riski
        ))
    
    return errors


def detect_defensive_line_break(
    defenders: List[TrackPoint], 
    threshold_m: float = TacticalConfig.DEFENSIVE_LINE_BREAK_THRESHOLD
) -> Optional[TacticalAlert]:
    """
    Savunma hattı bozulmasını tespit eder ve uyarı üretir.
    
    Args:
        defenders: Savunma oyuncularının tracking verileri
        threshold_m: Uyarı eşiği (metre)
        
    Returns:
        Optional[TacticalAlert]: Tespit edilen uyarı veya None
    """
    if len(defenders) < 3:
        return None
    
    line_errors = calculate_defensive_line_errors(defenders)
    max_error = max(error.line_error for error in line_errors)
    
    if max_error < threshold_m:
        return None
    
    # Güven skoru hesapla (0.0 - 1.0)
    confidence = min(1.0, max_error / 8.0)
    
    # Önem seviyesi belirle
    if max_error >= TacticalConfig.DEFENSIVE_LINE_BREAK_HIGH_THRESHOLD:
        severity = AlertSeverity.HIGH
    elif max_error >= threshold_m:
        severity = AlertSeverity.MEDIUM
    else:
        severity = AlertSeverity.LOW
    
    # Problemli oyuncuları bul
    problem_players = [
        error.player_id for error in line_errors 
        if error.line_error >= threshold_m
    ]
    
    return TacticalAlert(
        alert_type=AlertType.DEFENSIVE_LINE_BREAK,
        timestamp=defenders[0].timestamp,
        confidence=confidence,
        severity=severity,
        description=f"Savunma hattı bozulması tespit edildi. Maksimum sapma: {max_error:.1f}m",
        metadata={
            "max_error": max_error,
            "line_position": line_errors[0].line_x,
            "affected_players": len(problem_players),
            "threshold_used": threshold_m
        },
        player_ids=problem_players,
        team_id=defenders[0].team_id if defenders else None
    )


def analyze_offside_trap_effectiveness(
    defenders: List[TrackPoint],
    attacking_players: List[TrackPoint]
) -> Dict[str, any]:
    """
    Ofsayt tuzağının etkinliğini analiz eder.
    
    Args:
        defenders: Savunma oyuncularının tracking verileri
        attacking_players: Rakip forvet oyuncularının tracking verileri
        
    Returns:
        Dict: Ofsayt tuzağı analiz sonuçları
    """
    if len(defenders) < 2 or len(attacking_players) < 1:
        return {
            "trap_active": False,
            "effectiveness": 0.0,
            "offside_players": 0,
            "onside_players": len(attacking_players)
        }
    
    # Savunma hattının en ileri noktası
    defensive_line_x = max(d.x for d in defenders)
    
    # Ofsayt pozisyonundaki forvet oyuncuları
    offside_players = [
        p for p in attacking_players 
        if p.x > defensive_line_x
    ]
    
    onside_players = [
        p for p in attacking_players 
        if p.x <= defensive_line_x
    ]
    
    # Tuzak etkinliği hesapla
    total_attackers = len(attacking_players)
    offside_count = len(offside_players)
    effectiveness = offside_count / total_attackers if total_attackers > 0 else 0.0
    
    # Tuzak aktif mi kontrol et (savunma hattı düzgün mü?)
    line_errors = calculate_defensive_line_errors(defenders)
    max_line_error = max(error.line_error for error in line_errors) if line_errors else 0.0
    trap_active = max_line_error < TacticalConfig.DEFENSIVE_LINE_BREAK_THRESHOLD
    
    return {
        "trap_active": trap_active,
        "effectiveness": effectiveness,
        "offside_players": offside_count,
        "onside_players": len(onside_players),
        "defensive_line_x": defensive_line_x,
        "max_line_error": max_line_error
    }


def calculate_defensive_line_height(defenders: List[TrackPoint]) -> Dict[str, float]:
    """
    Savunma hattının sahada ne kadar ileri/geri olduğunu hesaplar.
    
    Args:
        defenders: Savunma oyuncularının tracking verileri
        
    Returns:
        Dict: Savunma hattı yükseklik metrikleri
    """
    if not defenders:
        return {
            "average_height": 0.0,
            "height_percentage": 0.0,
            "is_high_line": False,
            "is_deep_line": False
        }
    
    # Ortalama savunma hattı pozisyonu
    avg_height = np.mean([d.x for d in defenders])
    
    # Saha yüzdesi olarak hesapla (0-100%)
    field_length = TacticalConfig.FIELD_LENGTH
    height_percentage = (avg_height / field_length) * 100
    
    # Yüksek/alçak hat sınıflandırması
    is_high_line = height_percentage > 60  # Sahada %60'tan ileri
    is_deep_line = height_percentage < 30  # Sahada %30'dan geri
    
    return {
        "average_height": avg_height,
        "height_percentage": height_percentage,
        "is_high_line": is_high_line,
        "is_deep_line": is_deep_line
    }


def detect_defensive_line_movement_pattern(
    current_defenders: List[TrackPoint],
    previous_defenders: List[TrackPoint],
    time_diff: float
) -> Dict[str, any]:
    """
    Savunma hattının hareket desenini analiz eder.
    
    Args:
        current_defenders: Mevcut savunma pozisyonları
        previous_defenders: Önceki savunma pozisyonları
        time_diff: Zaman farkı (saniye)
        
    Returns:
        Dict: Hareket deseni analizi
    """
    if len(current_defenders) != len(previous_defenders) or time_diff <= 0:
        return {
            "movement_direction": "unknown",
            "movement_speed": 0.0,
            "synchronized": False
        }
    
    # Her oyuncu için hareket vektörü hesapla
    movements = []
    for curr, prev in zip(current_defenders, previous_defenders):
        if curr.player_id == prev.player_id:
            dx = curr.x - prev.x
            dy = curr.y - prev.y
            speed = np.sqrt(dx**2 + dy**2) / time_diff
            movements.append((dx, dy, speed))
    
    if not movements:
        return {
            "movement_direction": "unknown",
            "movement_speed": 0.0,
            "synchronized": False
        }
    
    # Ortalama hareket hesapla
    avg_dx = np.mean([m[0] for m in movements])
    avg_dy = np.mean([m[1] for m in movements])
    avg_speed = np.mean([m[2] for m in movements])
    
    # Hareket yönü belirle
    if abs(avg_dx) > abs(avg_dy):
        direction = "forward" if avg_dx > 0 else "backward"
    else:
        direction = "right" if avg_dy > 0 else "left"
    
    # Senkronizasyon kontrolü (oyuncular benzer hızda hareket ediyor mu?)
    speed_variance = np.var([m[2] for m in movements])
    synchronized = speed_variance < 1.0  # Düşük varyans = senkronize hareket
    
    return {
        "movement_direction": direction,
        "movement_speed": avg_speed,
        "synchronized": synchronized,
        "speed_variance": speed_variance
    }