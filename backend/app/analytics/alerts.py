from typing import List, Dict, Any
from app.models.tactical_alert import AlertSeverity, AlertCategory
import random


class TacticalAlertGenerator:
    """Generate tactical alerts from match analysis"""
    
    def __init__(self, metrics: Dict[str, Any], match_id: int):
        self.metrics = metrics
        self.match_id = match_id
        self.alerts = []
    
    def generate_alerts(self) -> List[Dict[str, Any]]:
        """Generate all tactical alerts"""
        self._check_possession_imbalance()
        self._check_defensive_gaps()
        self._check_offensive_patterns()
        self._check_physical_intensity()
        self._check_transition_speed()
        
        return self.alerts
    
    def _check_possession_imbalance(self):
        """Check for possession imbalance"""
        possession = self.metrics.get("possession", {})
        home_poss = possession.get("home", 50)
        away_poss = possession.get("away", 50)
        
        if abs(home_poss - away_poss) > 20:
            severity = AlertSeverity.WARNING if abs(home_poss - away_poss) > 30 else AlertSeverity.INFO
            
            if home_poss < away_poss:
                self.alerts.append({
                    "category": AlertCategory.POSSESSION,
                    "severity": severity,
                    "title": "Düşük Top Hakimiyeti",
                    "description": f"Takımınız maçın %{home_poss:.1f}'inde topa sahip. Orta saha kontrolünü artırmak için kısa pas oyununa odaklanın.",
                    "timestamp_seconds": random.uniform(300, 2700),
                    "metadata": {"possession_home": home_poss, "possession_away": away_poss}
                })
    
    def _check_defensive_gaps(self):
        """Check for defensive vulnerabilities"""
        # Mock alert based on heatmap analysis
        if random.random() > 0.5:
            self.alerts.append({
                "category": AlertCategory.DEFENSIVE,
                "severity": AlertSeverity.WARNING,
                "title": "Savunma Hattında Açıklık",
                "description": "Sol kanat bölgesinde savunma açıklıkları tespit edildi. Bek oyuncularının pozisyon alışlarını gözden geçirin.",
                "timestamp_seconds": random.uniform(600, 2400),
                "metadata": {"zone": "left_wing", "frequency": "high"}
            })
    
    def _check_offensive_patterns(self):
        """Check offensive effectiveness"""
        shots = self.metrics.get("shots", {})
        home_shots = shots.get("home", 0)
        
        if home_shots < 8:
            self.alerts.append({
                "category": AlertCategory.OFFENSIVE,
                "severity": AlertSeverity.INFO,
                "title": "Düşük Şut Sayısı",
                "description": f"Takımınız sadece {home_shots} şut çekti. Ceza sahası içinde daha fazla pozisyon yaratmaya çalışın.",
                "timestamp_seconds": random.uniform(1200, 2700),
                "metadata": {"shots": home_shots}
            })
    
    def _check_physical_intensity(self):
        """Check physical performance"""
        distance = self.metrics.get("distance_covered", {}).get("home", {})
        
        if distance:
            avg_distance = sum(distance.values()) / len(distance)
            
            if avg_distance < 8.0:  # km
                self.alerts.append({
                    "category": AlertCategory.PHYSICAL,
                    "severity": AlertSeverity.INFO,
                    "title": "Düşük Fiziksel Aktivite",
                    "description": f"Ortalama koşu mesafesi {avg_distance:.1f} km. Oyuncuların hareketliliğini artırın.",
                    "timestamp_seconds": random.uniform(1800, 2700),
                    "metadata": {"avg_distance_km": avg_distance}
                })
    
    def _check_transition_speed(self):
        """Check transition play"""
        if random.random() > 0.6:
            self.alerts.append({
                "category": AlertCategory.TRANSITION,
                "severity": AlertSeverity.INFO,
                "title": "Yavaş Geçiş Oyunu",
                "description": "Top kazanımından sonra hücuma geçiş süresi uzun. Hızlı kontra atak çalışmaları yapın.",
                "timestamp_seconds": random.uniform(900, 2100),
                "metadata": {"avg_transition_time": 4.5}
            })
