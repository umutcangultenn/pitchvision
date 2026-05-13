from typing import List, Dict, Any
from app.models.training_suggestion import TrainingCategory, TrainingPriority


class TrainingSuggestionGenerator:
    """Generate training suggestions based on match analysis"""
    
    def __init__(self, metrics: Dict[str, Any], alerts: List[Dict[str, Any]], match_id: int):
        self.metrics = metrics
        self.alerts = alerts
        self.match_id = match_id
        self.suggestions = []
    
    def generate_suggestions(self) -> List[Dict[str, Any]]:
        """Generate training suggestions"""
        self._analyze_technical_needs()
        self._analyze_tactical_needs()
        self._analyze_physical_needs()
        
        return self.suggestions
    
    def _analyze_technical_needs(self):
        """Analyze technical skill needs"""
        passes = self.metrics.get("passes", {})
        home_completed = passes.get("home_completed", 0)
        home_attempted = passes.get("home_attempted", 1)
        pass_accuracy = (home_completed / home_attempted) * 100 if home_attempted > 0 else 0
        
        if pass_accuracy < 75:
            self.suggestions.append({
                "match_id": self.match_id,
                "category": TrainingCategory.TECHNICAL,
                "priority": TrainingPriority.HIGH,
                "title": "Pas Doğruluğu Geliştirme",
                "description": f"Pas başarı oranı %{pass_accuracy:.1f}. Kısa ve orta mesafe pas çalışmaları yapılmalı.",
                "drill_suggestions": [
                    "Rondo çalışması (4v2, 5v2)",
                    "Üçgen pas oyunu",
                    "Dar alanda pas ve kontrol",
                    "Basınç altında pas yapma"
                ],
                "expected_improvement": "2-3 hafta içinde pas doğruluğunda %10-15 artış",
                "duration_minutes": 30
            })
    
    def _analyze_tactical_needs(self):
        """Analyze tactical needs"""
        possession = self.metrics.get("possession", {})
        home_poss = possession.get("home", 50)
        
        if home_poss < 45:
            self.suggestions.append({
                "match_id": self.match_id,
                "category": TrainingCategory.TACTICAL,
                "priority": TrainingPriority.HIGH,
                "title": "Top Hakimiyeti Stratejisi",
                "description": "Düşük top hakimiyeti. Pozisyonel oyun ve baskı çalışmaları gerekli.",
                "drill_suggestions": [
                    "Pozisyonel oyun 8v8",
                    "Baskı sonrası top kazanma",
                    "Saha genişliği kullanımı",
                    "Orta saha üstünlüğü kurma"
                ],
                "expected_improvement": "Top hakimiyetinde %5-10 artış",
                "duration_minutes": 45
            })
        
        # Check for defensive alerts
        defensive_alerts = [a for a in self.alerts if a.get("category") == "Savunma"]
        if defensive_alerts:
            self.suggestions.append({
                "match_id": self.match_id,
                "category": TrainingCategory.TACTICAL,
                "priority": TrainingPriority.MEDIUM,
                "title": "Savunma Organizasyonu",
                "description": "Savunma hattında açıklıklar tespit edildi. Kompakt savunma çalışması yapın.",
                "drill_suggestions": [
                    "Savunma hattı kaydırma",
                    "Bölgesel savunma",
                    "Kanat savunması",
                    "Geçiş anı savunma pozisyonu"
                ],
                "expected_improvement": "Savunma organizasyonunda iyileşme",
                "duration_minutes": 40
            })
    
    def _analyze_physical_needs(self):
        """Analyze physical conditioning needs"""
        distance = self.metrics.get("distance_covered", {}).get("home", {})
        
        if distance:
            avg_distance = sum(distance.values()) / len(distance)
            
            if avg_distance < 9.0:
                self.suggestions.append({
                    "match_id": self.match_id,
                    "category": TrainingCategory.PHYSICAL,
                    "priority": TrainingPriority.MEDIUM,
                    "title": "Dayanıklılık Geliştirme",
                    "description": f"Ortalama koşu mesafesi {avg_distance:.1f} km. Aerobik kapasite artırılmalı.",
                    "drill_suggestions": [
                        "Interval koşu (30-30, 15-15)",
                        "Topla dayanıklılık oyunu",
                        "Küçük sahada yüksek tempo",
                        "Aerobik eşik çalışması"
                    ],
                    "expected_improvement": "4 hafta içinde koşu mesafesinde %10-15 artış",
                    "duration_minutes": 35
                })
