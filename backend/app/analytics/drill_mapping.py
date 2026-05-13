"""
Drill mapping modülü.
Taktiksel uyarıları antrenman egzersizleriyle eşleştirir.
"""
from typing import List, Dict, Optional
from .types import TacticalAlert, AlertType, AlertSeverity, PlayerRole


class DrillRecommendation:
    """Antrenman egzersizi önerisi."""
    
    def __init__(
        self,
        name: str,
        description: str,
        duration_minutes: int,
        player_count: int,
        difficulty: str,
        focus_areas: List[str],
        equipment_needed: List[str] = None,
        coaching_points: List[str] = None
    ):
        self.name = name
        self.description = description
        self.duration_minutes = duration_minutes
        self.player_count = player_count
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.focus_areas = focus_areas
        self.equipment_needed = equipment_needed or []
        self.coaching_points = coaching_points or []


# Uyarı tipine göre drill veritabanı
DRILL_DATABASE = {
    AlertType.DEFENSIVE_LINE_BREAK: [
        DrillRecommendation(
            name="Savunma Hattı Senkronizasyonu",
            description="Savunma oyuncularının hat düzgünlüğünü koruma egzersizi",
            duration_minutes=20,
            player_count=8,
            difficulty="medium",
            focus_areas=["defensive_line", "communication", "positioning"],
            equipment_needed=["cones", "bibs"],
            coaching_points=[
                "Sürekli iletişim halinde olun",
                "En yavaş oyuncuya göre hareket edin",
                "Ofsayt tuzağı kurarken beraber çıkın"
            ]
        ),
        DrillRecommendation(
            name="4v2 Savunma Kompaktlığı",
            description="Dar alanda savunma hattı düzgünlüğü koruma",
            duration_minutes=15,
            player_count=6,
            difficulty="easy",
            focus_areas=["compactness", "pressure", "cover"],
            equipment_needed=["cones"],
            coaching_points=[
                "Mesafeleri koruyun",
                "Baskı-örtme prensibini uygulayın",
                "Yan pas yollarını kapatın"
            ]
        )
    ],
    
    AlertType.BLOCK_GAP_WIDE: [
        DrillRecommendation(
            name="Blok Mesafe Kontrolü",
            description="Savunma, orta saha ve forvet blokları arası mesafe ayarı",
            duration_minutes=25,
            player_count=11,
            difficulty="hard",
            focus_areas=["block_distance", "team_shape", "transition"],
            equipment_needed=["cones", "bibs", "markers"],
            coaching_points=[
                "Bloklar arası 15-20m mesafe koruyun",
                "Top kaybında hızla kompakt olun",
                "Orta saha oyuncuları köprü görevi yapın"
            ]
        ),
        DrillRecommendation(
            name="7v7 Kompakt Oyun",
            description="Küçük sahada kompakt takım oyunu geliştirme",
            duration_minutes=20,
            player_count=14,
            difficulty="medium",
            focus_areas=["compactness", "pressing", "support"],
            equipment_needed=["small_goals", "bibs"],
            coaching_points=[
                "Topa yakın oyuncular baskı yapsın",
                "Uzak oyuncular destek pozisyonu alsın",
                "Takım genişliği 25m'yi geçmesin"
            ]
        )
    ],
    
    AlertType.TRANSITION_SLOW: [
        DrillRecommendation(
            name="Hızlı Geçiş 3v2",
            description="Top kazanımından sonra hızlı kontra atak",
            duration_minutes=18,
            player_count=8,
            difficulty="medium",
            focus_areas=["counter_attack", "speed", "decision_making"],
            equipment_needed=["goals", "balls", "bibs"],
            coaching_points=[
                "İlk pas 3 saniye içinde",
                "Boş alanlara koşu yapın",
                "Basit ve hızlı paslar tercih edin"
            ]
        ),
        DrillRecommendation(
            name="Geçiş Kutuları",
            description="Farklı bölgelerde geçiş oyunu pratik",
            duration_minutes=22,
            player_count=12,
            difficulty="hard",
            focus_areas=["transition", "positioning", "tempo"],
            equipment_needed=["cones", "bibs", "balls"],
            coaching_points=[
                "Her bölgede farklı tempo",
                "Savunmadan hücuma 5 saniyede geçin",
                "Pozisyon değişimlerini hızlandırın"
            ]
        )
    ],
    
    AlertType.DEPTH_RUN_OPPORTUNITY: [
        DrillRecommendation(
            name="Derin Koşu Zamanlaması",
            description="Savunma arkasına koşu zamanlaması ve pas koordinasyonu",
            duration_minutes=20,
            player_count=8,
            difficulty="medium",
            focus_areas=["timing", "through_balls", "finishing"],
            equipment_needed=["cones", "goals", "balls"],
            coaching_points=[
                "Pas öncesi koşuya başlayın",
                "Ofsayt çizgisini takip edin",
                "İlk dokunuşla kontrolü sağlayın"
            ]
        ),
        DrillRecommendation(
            name="Bindirme ve Derin Pas",
            description="Kanat bindirmesi ile derin pas kombinasyonu",
            duration_minutes=25,
            player_count=10,
            difficulty="hard",
            focus_areas=["overlapping", "crossing", "movement"],
            equipment_needed=["cones", "goals", "balls", "bibs"],
            coaching_points=[
                "Bindirme zamanlamasını ayarlayın",
                "Merkeze ve kanada seçenek yaratın",
                "Savunma hattını gergin tutun"
            ]
        )
    ],
    
    AlertType.COMPACTNESS_LOST: [
        DrillRecommendation(
            name="Takım Şekli Koruma",
            description="Farklı durumlarda takım şeklini koruma egzersizi",
            duration_minutes=30,
            player_count=11,
            difficulty="hard",
            focus_areas=["team_shape", "communication", "discipline"],
            equipment_needed=["cones", "bibs", "markers"],
            coaching_points=[
                "Takım genişliği 40m'yi geçmesin",
                "Takım boyu 35m'yi geçmesin",
                "Merkez oyuncular referans noktası olsun"
            ]
        ),
        DrillRecommendation(
            name="Baskı Sonrası Kompaktlık",
            description="Baskı uyguladıktan sonra takım şeklini koruma",
            duration_minutes=20,
            player_count=9,
            difficulty="medium",
            focus_areas=["pressing", "recovery", "shape"],
            equipment_needed=["cones", "bibs"],
            coaching_points=[
                "Baskı sonrası hızla şekil alın",
                "Boşlukları kapatmaya odaklanın",
                "İkinci dalga savunması hazır olsun"
            ]
        )
    ]
}


def get_drill_recommendations(
    alert: TacticalAlert,
    team_level: str = "youth",  # "youth", "amateur", "professional"
    available_time: int = 30,  # dakika
    player_count: int = 11
) -> List[DrillRecommendation]:
    """
    Verilen uyarı için drill önerileri getirir.
    
    Args:
        alert: Taktiksel uyarı
        team_level: Takım seviyesi
        available_time: Mevcut antrenman süresi (dakika)
        player_count: Mevcut oyuncu sayısı
        
    Returns:
        List[DrillRecommendation]: Önerilen driller
    """
    # Uyarı tipine göre drilleri getir
    available_drills = DRILL_DATABASE.get(alert.alert_type, [])
    
    if not available_drills:
        return []
    
    # Filtreleme kriterleri
    suitable_drills = []
    
    for drill in available_drills:
        # Süre kontrolü
        if drill.duration_minutes > available_time:
            continue
        
        # Oyuncu sayısı kontrolü (±2 oyuncu toleransı)
        if abs(drill.player_count - player_count) > 2:
            continue
        
        # Seviye kontrolü
        if team_level == "youth" and drill.difficulty == "hard":
            continue
        elif team_level == "amateur" and drill.difficulty == "hard":
            # Amatör seviye için zor drilleri orta seviyeye düşür
            drill.difficulty = "medium"
        
        suitable_drills.append(drill)
    
    # Uyarı önem seviyesine göre sırala
    if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
        # Yüksek önemli uyarılar için daha yoğun driller öncelikli
        suitable_drills.sort(key=lambda d: d.duration_minutes, reverse=True)
    else:
        # Düşük önemli uyarılar için kısa driller öncelikli
        suitable_drills.sort(key=lambda d: d.duration_minutes)
    
    return suitable_drills[:3]  # En fazla 3 öneri


def create_training_session(
    alerts: List[TacticalAlert],
    session_duration: int = 90,  # dakika
    team_level: str = "youth",
    player_count: int = 11
) -> Dict[str, any]:
    """
    Uyarılara göre tam antrenman seansı oluşturur.
    
    Args:
        alerts: Taktiksel uyarılar listesi
        session_duration: Toplam antrenman süresi
        team_level: Takım seviyesi
        player_count: Oyuncu sayısı
        
    Returns:
        Dict: Antrenman seansı planı
    """
    # Uyarıları öncelik sırasına göre sırala
    sorted_alerts = sorted(
        alerts, 
        key=lambda a: (a.severity.value, a.confidence), 
        reverse=True
    )
    
    session_plan = {
        "total_duration": session_duration,
        "warm_up": {
            "duration": 15,
            "activities": ["Dynamic stretching", "Ball work", "Passing in pairs"]
        },
        "main_drills": [],
        "cool_down": {
            "duration": 10,
            "activities": ["Static stretching", "Recovery"]
        },
        "remaining_time": session_duration - 25  # Isınma ve soğuma hariç
    }
    
    used_time = 0
    remaining_time = session_plan["remaining_time"]
    
    # Her uyarı için drill ekle
    for alert in sorted_alerts[:4]:  # En fazla 4 uyarı işle
        if remaining_time <= 10:  # En az 10 dakika gerekli
            break
        
        recommendations = get_drill_recommendations(
            alert, team_level, remaining_time, player_count
        )
        
        if recommendations:
            selected_drill = recommendations[0]  # İlk öneriyi seç
            
            session_plan["main_drills"].append({
                "alert_type": alert.alert_type.value,
                "alert_description": alert.description,
                "drill": {
                    "name": selected_drill.name,
                    "description": selected_drill.description,
                    "duration": selected_drill.duration_minutes,
                    "player_count": selected_drill.player_count,
                    "difficulty": selected_drill.difficulty,
                    "focus_areas": selected_drill.focus_areas,
                    "equipment": selected_drill.equipment_needed,
                    "coaching_points": selected_drill.coaching_points
                }
            })
            
            used_time += selected_drill.duration_minutes
            remaining_time -= selected_drill.duration_minutes
    
    # Kalan süre için genel kondisyon/teknik çalışma
    if remaining_time > 15:
        session_plan["main_drills"].append({
            "alert_type": "general",
            "alert_description": "Genel teknik ve kondisyon",
            "drill": {
                "name": "Teknik Çember + Kondisyon",
                "description": "Pas tekniği ve fiziksel dayanıklılık çalışması",
                "duration": remaining_time,
                "player_count": player_count,
                "difficulty": "medium",
                "focus_areas": ["technique", "fitness"],
                "equipment": ["balls", "cones"],
                "coaching_points": [
                    "Pas kalitesini koruyun",
                    "Yüksek tempo sürdürün",
                    "İlk dokunuş kalitesine odaklanın"
                ]
            }
        })
    
    session_plan["actual_duration"] = session_duration - remaining_time + 25
    
    return session_plan


def get_drill_by_focus_area(focus_area: str) -> List[DrillRecommendation]:
    """
    Belirli bir odak alanına göre drilleri getirir.
    
    Args:
        focus_area: Odak alanı (örn: "defensive_line", "pressing")
        
    Returns:
        List[DrillRecommendation]: İlgili driller
    """
    matching_drills = []
    
    for alert_type, drills in DRILL_DATABASE.items():
        for drill in drills:
            if focus_area in drill.focus_areas:
                matching_drills.append(drill)
    
    return matching_drills


def get_equipment_list(drills: List[DrillRecommendation]) -> List[str]:
    """
    Drill listesi için gerekli ekipman listesi oluşturur.
    
    Args:
        drills: Drill listesi
        
    Returns:
        List[str]: Gerekli ekipmanlar
    """
    equipment_set = set()
    
    for drill in drills:
        equipment_set.update(drill.equipment_needed)
    
    return sorted(list(equipment_set))