"""
Taktiksel uyarı sistemi.
Maç sırasında gerçek zamanlı taktiksel uyarılar üretir.
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .types import (
    TrackPoint, TacticalAlert, AlertType, AlertSeverity, 
    PlayerRole, TacticalConfig
)
from .team_shape import calculate_team_shape, calculate_block_gaps
from .defensive_line import detect_defensive_line_break, calculate_defensive_line_errors
from .transitions import detect_slow_transition_alert, analyze_team_transition
from .runs import detect_depth_run_candidate, analyze_wing_overload


def generate_tactical_alerts(
    match_tracking_data: List[TrackPoint],
    team_id: int,
    timestamp: float,
    ball_position: Optional[Tuple[float, float]] = None
) -> List[TacticalAlert]:
    """
    Verilen tracking verisinden taktiksel uyarılar üretir.
    
    Args:
        match_tracking_data: Maç tracking verileri
        team_id: Analiz edilecek takım ID'si
        timestamp: Mevcut zaman damgası
        ball_position: Top pozisyonu (x, y)
        
    Returns:
        List[TacticalAlert]: Üretilen uyarılar listesi
    """
    alerts = []
    
    # Takım oyuncularını filtrele
    team_players = [p for p in match_tracking_data if p.team_id == team_id]
    
    if not team_players:
        return alerts
    
    # Pozisyon gruplarına ayır
    defenders = [p for p in team_players if p.role == PlayerRole.DEFENDER]
    midfielders = [p for p in team_players if p.role == PlayerRole.MIDFIELDER]
    forwards = [p for p in team_players if p.role == PlayerRole.FORWARD]
    
    # 1. Savunma hattı bozulması kontrolü
    if len(defenders) >= 3:
        defensive_alert = detect_defensive_line_break(defenders)
        if defensive_alert:
            alerts.append(defensive_alert)
    
    # 2. Blok mesafe kontrolü
    if defenders and midfielders:
        block_gaps = calculate_block_gaps(team_players)
        block_alert = detect_block_gap_alert(
            block_gaps.defensive_midfield_gap,
            block_gaps.midfield_forward_gap,
            team_id,
            timestamp
        )
        if block_alert:
            alerts.append(block_alert)
    
    # 3. Kompaktlık kontrolü
    team_shape = calculate_team_shape(team_players)
    compactness_alert = detect_compactness_alert(
        team_shape.compactness, team_id, timestamp
    )
    if compactness_alert:
        alerts.append(compactness_alert)
    
    # 4. Geçiş hızı kontrolü (basit versiyon)
    if ball_position and len(team_players) >= 6:
        transition_alert = detect_slow_transition_alert(
            team_players, ball_position, timestamp
        )
        if transition_alert:
            alerts.append(transition_alert)
    
    # 5. Derin koşu fırsatları
    if defenders and forwards:
        # Karşı takım savunma hattını bul
        opponent_defenders = [
            p for p in match_tracking_data 
            if p.team_id != team_id and p.role == PlayerRole.DEFENDER
        ]
        
        if opponent_defenders:
            defensive_line_x = np.mean([d.x for d in opponent_defenders])
            
            for forward in forwards:
                depth_run_alert = detect_depth_run_candidate(
                    forward, defensive_line_x, ball_position
                )
                if depth_run_alert:
                    alerts.append(depth_run_alert)
    
    return alerts


def detect_block_gap_alert(
    dm_gap: float,
    mf_gap: float,
    team_id: int,
    timestamp: float
) -> Optional[TacticalAlert]:
    """
    Bloklar arası mesafe uyarısı tespit eder.
    
    Args:
        dm_gap: Savunma-orta saha mesafesi
        mf_gap: Orta saha-forvet mesafesi
        team_id: Takım ID'si
        timestamp: Zaman damgası
        
    Returns:
        Optional[TacticalAlert]: Uyarı varsa TacticalAlert
    """
    max_gap = max(dm_gap, mf_gap)
    
    if max_gap < TacticalConfig.BLOCK_GAP_WARNING_THRESHOLD:
        return None
    
    # Önem seviyesi belirle
    if max_gap >= TacticalConfig.BLOCK_GAP_CRITICAL_THRESHOLD:
        severity = AlertSeverity.HIGH
        confidence = min(1.0, max_gap / 40.0)
    else:
        severity = AlertSeverity.MEDIUM
        confidence = min(0.8, max_gap / 30.0)
    
    description = f"Bloklar arası mesafe geniş: {max_gap:.1f}m"
    if dm_gap > mf_gap:
        description += " (Savunma-Orta saha)"
    else:
        description += " (Orta saha-Forvet)"
    
    return TacticalAlert(
        alert_type=AlertType.BLOCK_GAP_WIDE,
        timestamp=timestamp,
        confidence=confidence,
        severity=severity,
        description=description,
        metadata={
            "dm_gap": dm_gap,
            "mf_gap": mf_gap,
            "max_gap": max_gap
        },
        team_id=team_id
    )


def detect_compactness_alert(
    compactness: float,
    team_id: int,
    timestamp: float
) -> Optional[TacticalAlert]:
    """
    Takım kompaktlığı uyarısı tespit eder.
    
    Args:
        compactness: Kompaktlık değeri (metre)
        team_id: Takım ID'si
        timestamp: Zaman damgası
        
    Returns:
        Optional[TacticalAlert]: Uyarı varsa TacticalAlert
    """
    if compactness < TacticalConfig.COMPACTNESS_WARNING_THRESHOLD:
        return None
    
    # Önem seviyesi belirle
    if compactness >= TacticalConfig.COMPACTNESS_CRITICAL_THRESHOLD:
        severity = AlertSeverity.HIGH
        confidence = min(1.0, compactness / 35.0)
    else:
        severity = AlertSeverity.MEDIUM
        confidence = min(0.8, compactness / 25.0)
    
    return TacticalAlert(
        alert_type=AlertType.COMPACTNESS_LOST,
        timestamp=timestamp,
        confidence=confidence,
        severity=severity,
        description=f"Takım kompaktlığı kaybı: {compactness:.1f}m ortalama mesafe",
        metadata={
            "compactness": compactness,
            "threshold": TacticalConfig.COMPACTNESS_WARNING_THRESHOLD
        },
        team_id=team_id
    )


def filter_alerts_by_priority(
    alerts: List[TacticalAlert],
    max_alerts: int = 5
) -> List[TacticalAlert]:
    """
    Uyarıları öncelik sırasına göre filtreler.
    
    Args:
        alerts: Uyarı listesi
        max_alerts: Maksimum uyarı sayısı
        
    Returns:
        List[TacticalAlert]: Filtrelenmiş uyarılar
    """
    if not alerts:
        return []
    
    # Öncelik skoru hesapla (severity + confidence)
    def priority_score(alert: TacticalAlert) -> float:
        severity_weights = {
            AlertSeverity.LOW: 1.0,
            AlertSeverity.MEDIUM: 2.0,
            AlertSeverity.HIGH: 3.0,
            AlertSeverity.CRITICAL: 4.0
        }
        return severity_weights[alert.severity] * alert.confidence
    
    # Öncelik sırasına göre sırala
    sorted_alerts = sorted(alerts, key=priority_score, reverse=True)
    
    return sorted_alerts[:max_alerts]


def create_alert_summary(alerts: List[TacticalAlert]) -> Dict[str, any]:
    """
    Uyarılardan özet rapor oluşturur.
    
    Args:
        alerts: Uyarı listesi
        
    Returns:
        Dict: Özet rapor
    """
    if not alerts:
        return {
            "total_alerts": 0,
            "by_severity": {},
            "by_type": {},
            "most_frequent": None,
            "highest_priority": None
        }
    
    # Önem seviyesine göre grupla
    by_severity = {}
    for alert in alerts:
        severity = alert.severity.value
        by_severity[severity] = by_severity.get(severity, 0) + 1
    
    # Tipe göre grupla
    by_type = {}
    for alert in alerts:
        alert_type = alert.alert_type.value
        by_type[alert_type] = by_type.get(alert_type, 0) + 1
    
    # En sık görülen tip
    most_frequent = max(by_type.items(), key=lambda x: x[1]) if by_type else None
    
    # En yüksek öncelikli
    highest_priority = max(alerts, key=lambda a: a.confidence * 
                          (4 if a.severity == AlertSeverity.CRITICAL else
                           3 if a.severity == AlertSeverity.HIGH else
                           2 if a.severity == AlertSeverity.MEDIUM else 1))
    
    return {
        "total_alerts": len(alerts),
        "by_severity": by_severity,
        "by_type": by_type,
        "most_frequent": {
            "type": most_frequent[0],
            "count": most_frequent[1]
        } if most_frequent else None,
        "highest_priority": {
            "type": highest_priority.alert_type.value,
            "severity": highest_priority.severity.value,
            "confidence": highest_priority.confidence,
            "description": highest_priority.description
        } if highest_priority else None
    }