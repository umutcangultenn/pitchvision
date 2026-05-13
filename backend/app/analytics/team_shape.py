"""
Takım şekli analizi modülü.
Oyuncu pozisyonlarından takım geometrisini hesaplar.
"""
import numpy as np
from typing import List, Dict, Tuple
from .types import TrackPoint, TeamShape, BlockGaps, PlayerRole, TacticalConfig


def calculate_team_shape(points: List[TrackPoint]) -> TeamShape:
    """
    Verilen oyuncu pozisyonlarından takım şeklini hesaplar.
    
    Args:
        points: Oyuncu tracking verileri listesi
        
    Returns:
        TeamShape: Takım şekli metrikleri
    """
    if not points:
        raise ValueError("En az bir oyuncu verisi gerekli")
    
    # Koordinatları numpy array'e çevir
    positions = np.array([(p.x, p.y) for p in points])
    
    # Takım boyutları
    x_coords = positions[:, 0]
    y_coords = positions[:, 1]
    
    team_length = float(np.max(x_coords) - np.min(x_coords))
    team_width = float(np.max(y_coords) - np.min(y_coords))
    
    # Merkez nokta (centroid)
    centroid_x = float(np.mean(x_coords))
    centroid_y = float(np.mean(y_coords))
    
    # Kompaktlık: oyuncuların merkez noktadan ortalama uzaklığı
    distances = np.sqrt((x_coords - centroid_x)**2 + (y_coords - centroid_y)**2)
    compactness = float(np.mean(distances))
    
    return TeamShape(
        team_length=team_length,
        team_width=team_width,
        centroid_x=centroid_x,
        centroid_y=centroid_y,
        compactness=compactness
    )


def calculate_block_gaps(points: List[TrackPoint]) -> BlockGaps:
    """
    Savunma, orta saha ve forvet blokları arasındaki mesafeleri hesaplar.
    
    Args:
        points: Oyuncu tracking verileri listesi
        
    Returns:
        BlockGaps: Bloklar arası mesafeler
    """
    # Oyuncuları rollerine göre grupla
    defenders = [p for p in points if p.role == PlayerRole.DEFENDER]
    midfielders = [p for p in points if p.role == PlayerRole.MIDFIELDER]
    forwards = [p for p in points if p.role == PlayerRole.FORWARD]
    
    # Her blok için ortalama x pozisyonu hesapla
    def get_block_average_x(block_points: List[TrackPoint]) -> float:
        if not block_points:
            return 0.0
        return np.mean([p.x for p in block_points])
    
    def_avg_x = get_block_average_x(defenders)
    mid_avg_x = get_block_average_x(midfielders)
    fwd_avg_x = get_block_average_x(forwards)
    
    # Bloklar arası mesafeleri hesapla
    defensive_midfield_gap = abs(mid_avg_x - def_avg_x) if defenders and midfielders else 0.0
    midfield_forward_gap = abs(fwd_avg_x - mid_avg_x) if midfielders and forwards else 0.0
    
    return BlockGaps(
        defensive_midfield_gap=defensive_midfield_gap,
        midfield_forward_gap=midfield_forward_gap
    )


def calculate_team_width_by_thirds(points: List[TrackPoint]) -> Dict[str, float]:
    """
    Sahanın üçte birlik bölümlerine göre takım genişliğini hesaplar.
    
    Args:
        points: Oyuncu tracking verileri listesi
        
    Returns:
        Dict: Her üçte birlik bölüm için genişlik değerleri
    """
    if not points:
        return {"defensive_third": 0.0, "middle_third": 0.0, "attacking_third": 0.0}
    
    # Sahanın üçte birlik bölümlerini tanımla
    field_length = TacticalConfig.FIELD_LENGTH
    defensive_third = field_length / 3
    attacking_third = 2 * field_length / 3
    
    # Oyuncuları bölümlere göre grupla
    def_third_players = [p for p in points if p.x <= defensive_third]
    mid_third_players = [p for p in points if defensive_third < p.x <= attacking_third]
    att_third_players = [p for p in points if p.x > attacking_third]
    
    def calculate_width(players: List[TrackPoint]) -> float:
        if len(players) < 2:
            return 0.0
        y_coords = [p.y for p in players]
        return max(y_coords) - min(y_coords)
    
    return {
        "defensive_third": calculate_width(def_third_players),
        "middle_third": calculate_width(mid_third_players),
        "attacking_third": calculate_width(att_third_players)
    }


def calculate_formation_compactness(points: List[TrackPoint]) -> Dict[str, float]:
    """
    Pozisyon gruplarına göre kompaktlık hesaplar.
    
    Args:
        points: Oyuncu tracking verileri listesi
        
    Returns:
        Dict: Her pozisyon grubu için kompaktlık değerleri
    """
    result = {}
    
    # Pozisyon gruplarına göre ayır
    position_groups = {
        "defenders": [p for p in points if p.role == PlayerRole.DEFENDER],
        "midfielders": [p for p in points if p.role == PlayerRole.MIDFIELDER],
        "forwards": [p for p in points if p.role == PlayerRole.FORWARD]
    }
    
    for group_name, group_points in position_groups.items():
        if len(group_points) < 2:
            result[group_name] = 0.0
            continue
            
        # Grup merkezi hesapla
        positions = np.array([(p.x, p.y) for p in group_points])
        centroid = np.mean(positions, axis=0)
        
        # Ortalama mesafe hesapla
        distances = np.sqrt(np.sum((positions - centroid)**2, axis=1))
        result[group_name] = float(np.mean(distances))
    
    return result


def detect_formation_pattern(points: List[TrackPoint]) -> Dict[str, any]:
    """
    Oyuncu pozisyonlarından formasyon desenini tespit etmeye çalışır.
    
    Args:
        points: Oyuncu tracking verileri listesi
        
    Returns:
        Dict: Tespit edilen formasyon bilgileri
    """
    # Kaleci hariç oyuncuları al
    field_players = [p for p in points if p.role != PlayerRole.GOALKEEPER]
    
    if len(field_players) < 10:
        return {"formation": "unknown", "confidence": 0.0}
    
    # Pozisyon sayılarını hesapla
    def_count = len([p for p in field_players if p.role == PlayerRole.DEFENDER])
    mid_count = len([p for p in field_players if p.role == PlayerRole.MIDFIELDER])
    fwd_count = len([p for p in field_players if p.role == PlayerRole.FORWARD])
    
    # Yaygın formasyonları kontrol et
    formations = {
        (4, 4, 2): "4-4-2",
        (4, 3, 3): "4-3-3",
        (3, 5, 2): "3-5-2",
        (5, 3, 2): "5-3-2",
        (4, 5, 1): "4-5-1",
        (3, 4, 3): "3-4-3"
    }
    
    formation_key = (def_count, mid_count, fwd_count)
    formation_name = formations.get(formation_key, f"{def_count}-{mid_count}-{fwd_count}")
    
    # Güven skoru hesapla (basit heuristik)
    confidence = 0.8 if formation_key in formations else 0.4
    
    return {
        "formation": formation_name,
        "confidence": confidence,
        "defender_count": def_count,
        "midfielder_count": mid_count,
        "forward_count": fwd_count
    }