"""
Oyuncu performans skorları hesaplama modülü.
Taktiksel, teknik, fiziksel ve karar verme skorlarını hesaplar.
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from .types import TrackPoint, PlayerRole, TacticalConfig


def calculate_tactical_score(
    player_positions: List[TrackPoint],
    team_positions: List[TrackPoint],
    opponent_positions: List[TrackPoint]
) -> float:
    """
    Oyuncunun taktiksel skorunu hesaplar.
    
    Args:
        player_positions: Oyuncunun pozisyon geçmişi
        team_positions: Takım arkadaşlarının pozisyonları
        opponent_positions: Rakip oyuncuların pozisyonları
        
    Returns:
        float: Taktiksel skor (0-10)
    """
    if not player_positions:
        return 0.0
    
    score_components = []
    
    # 1. Pozisyon disiplini (0-2.5 puan)
    position_score = calculate_position_discipline(player_positions)
    score_components.append(position_score * 2.5)
    
    # 2. Takım kompaktlığına katkı (0-2.5 puan)
    compactness_score = calculate_compactness_contribution(
        player_positions, team_positions
    )
    score_components.append(compactness_score * 2.5)
    
    # 3. Savunma katkısı (0-2.5 puan)
    defensive_score = calculate_defensive_contribution(
        player_positions, opponent_positions
    )
    score_components.append(defensive_score * 2.5)
    
    # 4. Hücum katkısı (0-2.5 puan)
    offensive_score = calculate_offensive_contribution(
        player_positions, team_positions
    )
    score_components.append(offensive_score * 2.5)
    
    return min(10.0, sum(score_components))


def calculate_position_discipline(player_positions: List[TrackPoint]) -> float:
    """
    Oyuncunun pozisyon disiplinini hesaplar.
    
    Args:
        player_positions: Oyuncunun pozisyon geçmişi
        
    Returns:
        float: Pozisyon disiplini skoru (0-1)
    """
    if len(player_positions) < 2:
        return 0.5
    
    # Ortalama pozisyon hesapla
    avg_x = np.mean([p.x for p in player_positions])
    avg_y = np.mean([p.y for p in player_positions])
    
    # Pozisyondan sapmaları hesapla
    deviations = []
    for pos in player_positions:
        deviation = np.sqrt((pos.x - avg_x)**2 + (pos.y - avg_y)**2)
        deviations.append(deviation)
    
    avg_deviation = np.mean(deviations)
    
    # Pozisyona göre beklenen sapma
    role = player_positions[0].role
    expected_deviation = {
        PlayerRole.DEFENDER: 15.0,  # Savunma oyuncuları daha az hareket eder
        PlayerRole.MIDFIELDER: 20.0,  # Orta saha oyuncuları orta düzeyde
        PlayerRole.FORWARD: 25.0,  # Forvet oyuncuları daha çok hareket eder
        PlayerRole.GOALKEEPER: 8.0  # Kaleci en az hareket eder
    }.get(role, 20.0)
    
    # Skor hesapla (düşük sapma = yüksek disiplin)
    if avg_deviation <= expected_deviation:
        return 1.0
    else:
        return max(0.0, 1.0 - (avg_deviation - expected_deviation) / expected_deviation)


def calculate_compactness_contribution(
    player_positions: List[TrackPoint],
    team_positions: List[TrackPoint]
) -> float:
    """
    Oyuncunun takım kompaktlığına katkısını hesaplar.
    
    Args:
        player_positions: Oyuncunun pozisyonları
        team_positions: Takım pozisyonları
        
    Returns:
        float: Kompaktlık katkısı skoru (0-1)
    """
    if not player_positions or not team_positions:
        return 0.5
    
    # Son pozisyonu al
    player_pos = player_positions[-1]
    
    # Takım merkezini hesapla
    team_x = np.mean([p.x for p in team_positions])
    team_y = np.mean([p.y for p in team_positions])
    
    # Oyuncunun takım merkezine uzaklığı
    distance_to_center = np.sqrt(
        (player_pos.x - team_x)**2 + (player_pos.y - team_y)**2
    )
    
    # İdeal mesafe (pozisyona göre)
    ideal_distance = {
        PlayerRole.DEFENDER: 12.0,
        PlayerRole.MIDFIELDER: 8.0,
        PlayerRole.FORWARD: 15.0,
        PlayerRole.GOALKEEPER: 25.0
    }.get(player_pos.role, 12.0)
    
    # Skor hesapla
    if distance_to_center <= ideal_distance:
        return 1.0
    else:
        return max(0.0, 1.0 - (distance_to_center - ideal_distance) / ideal_distance)


def calculate_defensive_contribution(
    player_positions: List[TrackPoint],
    opponent_positions: List[TrackPoint]
) -> float:
    """
    Oyuncunun savunma katkısını hesaplar.
    
    Args:
        player_positions: Oyuncunun pozisyonları
        opponent_positions: Rakip oyuncuların pozisyonları
        
    Returns:
        float: Savunma katkısı skoru (0-1)
    """
    if not player_positions or not opponent_positions:
        return 0.5
    
    player_pos = player_positions[-1]
    
    # Yakındaki rakip oyuncular (20m içinde)
    nearby_opponents = []
    for opp in opponent_positions:
        distance = np.sqrt(
            (player_pos.x - opp.x)**2 + (player_pos.y - opp.y)**2
        )
        if distance <= 20.0:
            nearby_opponents.append((opp, distance))
    
    if not nearby_opponents:
        return 0.3  # Rakip yok, orta skor
    
    # En yakın rakibe mesafe
    closest_distance = min(dist for _, dist in nearby_opponents)
    
    # Savunma skoru (yakın mesafe = yüksek savunma katkısı)
    if closest_distance <= 3.0:
        return 1.0  # Çok yakın baskı
    elif closest_distance <= 8.0:
        return 0.8  # İyi baskı
    elif closest_distance <= 15.0:
        return 0.6  # Orta baskı
    else:
        return 0.3  # Zayıf baskı


def calculate_offensive_contribution(
    player_positions: List[TrackPoint],
    team_positions: List[TrackPoint]
) -> float:
    """
    Oyuncunun hücum katkısını hesaplar.
    
    Args:
        player_positions: Oyuncunun pozisyonları
        team_positions: Takım pozisyonları
        
    Returns:
        float: Hücum katkısı skoru (0-1)
    """
    if len(player_positions) < 2:
        return 0.5
    
    # İleri hareket analizi
    current_pos = player_positions[-1]
    previous_pos = player_positions[-2]
    
    forward_movement = current_pos.x - previous_pos.x
    
    # Pozisyona göre beklenen hareket
    role = current_pos.role
    if role == PlayerRole.FORWARD:
        # Forvet oyuncuları için ileri hareket pozitif
        if forward_movement > 2.0:
            return 1.0
        elif forward_movement > 0:
            return 0.7
        else:
            return 0.3
    elif role == PlayerRole.MIDFIELDER:
        # Orta saha oyuncuları için dengeli hareket
        if abs(forward_movement) < 5.0:
            return 0.8  # Dengeli pozisyon
        else:
            return 0.5
    else:
        # Savunma oyuncuları için geri hareket normal
        if forward_movement < -1.0:
            return 0.7  # Savunma pozisyonunda
        else:
            return 0.5


def calculate_physical_score(player_positions: List[TrackPoint]) -> float:
    """
    Oyuncunun fiziksel skorunu hesaplar.
    
    Args:
        player_positions: Oyuncunun pozisyon geçmişi
        
    Returns:
        float: Fiziksel skor (0-10)
    """
    if len(player_positions) < 2:
        return 5.0
    
    # Hız analizi
    speeds = []
    distances = []
    
    for i in range(1, len(player_positions)):
        curr = player_positions[i]
        prev = player_positions[i-1]
        
        time_diff = curr.timestamp - prev.timestamp
        if time_diff > 0:
            distance = np.sqrt(
                (curr.x - prev.x)**2 + (curr.y - prev.y)**2
            )
            speed = distance / time_diff
            
            speeds.append(speed)
            distances.append(distance)
    
    if not speeds:
        return 5.0
    
    # Fiziksel metrikler
    max_speed = max(speeds) if speeds else 0
    avg_speed = np.mean(speeds) if speeds else 0
    total_distance = sum(distances) if distances else 0
    
    # Skor bileşenleri
    speed_score = min(4.0, max_speed / 2.0)  # Maks hız (0-4 puan)
    endurance_score = min(3.0, avg_speed / 1.5)  # Dayanıklılık (0-3 puan)
    activity_score = min(3.0, total_distance / 100.0)  # Aktivite (0-3 puan)
    
    return speed_score + endurance_score + activity_score


def calculate_decision_score(
    player_positions: List[TrackPoint],
    team_positions: List[TrackPoint],
    ball_events: List[Dict] = None
) -> float:
    """
    Oyuncunun karar verme skorunu hesaplar.
    
    Args:
        player_positions: Oyuncunun pozisyonları
        team_positions: Takım pozisyonları
        ball_events: Top olayları (pas, şut, vs.)
        
    Returns:
        float: Karar verme skoru (0-10)
    """
    if not player_positions:
        return 5.0
    
    # Basit karar verme analizi (gerçek implementasyonda top olayları gerekli)
    score_components = []
    
    # 1. Pozisyon seçimi (0-3 puan)
    position_choice_score = analyze_position_choices(player_positions, team_positions)
    score_components.append(position_choice_score * 3.0)
    
    # 2. Zamanlama (0-3 puan)
    timing_score = analyze_movement_timing(player_positions)
    score_components.append(timing_score * 3.0)
    
    # 3. Risk yönetimi (0-4 puan)
    risk_score = analyze_risk_management(player_positions)
    score_components.append(risk_score * 4.0)
    
    return min(10.0, sum(score_components))


def analyze_position_choices(
    player_positions: List[TrackPoint],
    team_positions: List[TrackPoint]
) -> float:
    """Pozisyon seçimi kalitesini analiz eder."""
    if len(player_positions) < 3:
        return 0.5
    
    # Son 3 pozisyondaki tutarlılık
    recent_positions = player_positions[-3:]
    
    # Pozisyon değişikliklerinin mantıklılığı
    position_changes = []
    for i in range(1, len(recent_positions)):
        curr = recent_positions[i]
        prev = recent_positions[i-1]
        
        change = np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2)
        position_changes.append(change)
    
    avg_change = np.mean(position_changes) if position_changes else 0
    
    # Optimal değişim aralığı (2-8 metre)
    if 2.0 <= avg_change <= 8.0:
        return 1.0  # İyi pozisyon seçimi
    elif avg_change < 2.0:
        return 0.6  # Çok statik
    else:
        return 0.4  # Çok hareketli


def analyze_movement_timing(player_positions: List[TrackPoint]) -> float:
    """Hareket zamanlamasını analiz eder."""
    if len(player_positions) < 2:
        return 0.5
    
    # Hız değişimlerinin düzgünlüğü
    speed_changes = []
    
    for i in range(2, len(player_positions)):
        curr = player_positions[i]
        prev = player_positions[i-1]
        prev2 = player_positions[i-2]
        
        # Hız hesapla
        time_diff1 = curr.timestamp - prev.timestamp
        time_diff2 = prev.timestamp - prev2.timestamp
        
        if time_diff1 > 0 and time_diff2 > 0:
            speed1 = np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2) / time_diff1
            speed2 = np.sqrt((prev.x - prev2.x)**2 + (prev.y - prev2.y)**2) / time_diff2
            
            speed_change = abs(speed1 - speed2)
            speed_changes.append(speed_change)
    
    if not speed_changes:
        return 0.5
    
    # Düzgün hız değişimi = iyi zamanlama
    avg_speed_change = np.mean(speed_changes)
    
    if avg_speed_change < 1.0:
        return 1.0  # Çok düzgün
    elif avg_speed_change < 2.0:
        return 0.8  # İyi
    elif avg_speed_change < 3.0:
        return 0.6  # Orta
    else:
        return 0.3  # Zayıf


def analyze_risk_management(player_positions: List[TrackPoint]) -> float:
    """Risk yönetimi kalitesini analiz eder."""
    if not player_positions:
        return 0.5
    
    player_pos = player_positions[-1]
    
    # Saha pozisyonuna göre risk değerlendirmesi
    field_length = TacticalConfig.FIELD_LENGTH
    field_width = TacticalConfig.FIELD_WIDTH
    
    # Saha kenarlarına yakınlık riski
    edge_risk = 0.0
    if player_pos.y < field_width * 0.1 or player_pos.y > field_width * 0.9:
        edge_risk = 0.3  # Kenar riski
    
    # Pozisyona göre risk toleransı
    role = player_pos.role
    if role == PlayerRole.DEFENDER:
        # Savunma oyuncuları düşük risk almalı
        if player_pos.x < field_length * 0.4:  # Kendi yarı sahada
            risk_score = 1.0 - edge_risk
        else:
            risk_score = 0.5 - edge_risk  # İleri pozisyon riskli
    elif role == PlayerRole.MIDFIELDER:
        # Orta saha oyuncuları dengeli risk alabilir
        risk_score = 0.8 - edge_risk
    else:  # FORWARD
        # Forvet oyuncuları yüksek risk alabilir
        risk_score = 0.9 - edge_risk * 0.5
    
    return max(0.0, min(1.0, risk_score))