"""
Tactical Analytics Service.
API katmanı ile analytics engine arasında köprü görevi görür.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

from .types import TrackPoint, PlayerRole, TacticalAlert, AlertType, AlertSeverity
from .alerts_new import generate_tactical_alerts, filter_alerts_by_priority, create_alert_summary
from .team_shape import calculate_team_shape, calculate_block_gaps
from .player_scores import calculate_tactical_score, calculate_physical_score, calculate_decision_score
from .drill_mapping import get_drill_recommendations, create_training_session


class TacticalAnalyticsService:
    """Taktiksel analiz servisi."""
    
    def __init__(self):
        self.cache = {}  # Basit cache mekanizması
    
    def analyze_match_frame(
        self,
        match_id: int,
        frame_data: List[Dict[str, Any]],
        timestamp: float,
        ball_position: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Tek bir maç frame'ini analiz eder.
        
        Args:
            match_id: Maç ID'si
            frame_data: Frame verisi (dict listesi)
            timestamp: Zaman damgası
            ball_position: Top pozisyonu (x, y)
            
        Returns:
            Dict: Analiz sonuçları
        """
        # Dict verilerini TrackPoint'e çevir
        tracking_points = self._convert_to_track_points(frame_data, timestamp)
        
        if not tracking_points:
            return {"error": "Geçersiz tracking verisi"}
        
        # Her takım için analiz yap
        results = {
            "match_id": match_id,
            "timestamp": timestamp,
            "teams": {}
        }
        
        team_ids = list(set(p.team_id for p in tracking_points))
        
        for team_id in team_ids:
            team_analysis = self._analyze_team(
                tracking_points, team_id, timestamp, ball_position
            )
            results["teams"][team_id] = team_analysis
        
        return results
    
    def _convert_to_track_points(
        self, 
        frame_data: List[Dict[str, Any]], 
        timestamp: float
    ) -> List[TrackPoint]:
        """Frame verisini TrackPoint listesine çevirir."""
        track_points = []
        
        for data in frame_data:
            try:
                # Role string'ini enum'a çevir
                role_str = data.get("role", "midfielder").lower()
                role_mapping = {
                    "goalkeeper": PlayerRole.GOALKEEPER,
                    "defender": PlayerRole.DEFENDER,
                    "midfielder": PlayerRole.MIDFIELDER,
                    "forward": PlayerRole.FORWARD
                }
                role = role_mapping.get(role_str, PlayerRole.MIDFIELDER)
                
                point = TrackPoint(
                    player_id=data["player_id"],
                    team_id=data["team_id"],
                    role=role,
                    timestamp=timestamp,
                    x=float(data["x"]),
                    y=float(data["y"]),
                    speed=data.get("speed"),
                    vx=data.get("vx"),
                    vy=data.get("vy")
                )
                track_points.append(point)
                
            except (KeyError, ValueError, TypeError) as e:
                # Hatalı veriyi atla
                continue
        
        return track_points
    
    def _analyze_team(
        self,
        tracking_points: List[TrackPoint],
        team_id: int,
        timestamp: float,
        ball_position: Optional[tuple]
    ) -> Dict[str, Any]:
        """Tek takım analizi yapar."""
        team_players = [p for p in tracking_points if p.team_id == team_id]
        
        if not team_players:
            return {"error": "Takım verisi bulunamadı"}
        
        analysis = {
            "team_id": team_id,
            "player_count": len(team_players),
            "team_shape": {},
            "block_gaps": {},
            "alerts": [],
            "player_scores": {}
        }
        
        try:
            # Takım şekli
            team_shape = calculate_team_shape(team_players)
            analysis["team_shape"] = {
                "length": round(team_shape.team_length, 1),
                "width": round(team_shape.team_width, 1),
                "compactness": round(team_shape.compactness, 1),
                "centroid": {
                    "x": round(team_shape.centroid_x, 1),
                    "y": round(team_shape.centroid_y, 1)
                }
            }
            
            # Blok mesafeleri
            block_gaps = calculate_block_gaps(team_players)
            analysis["block_gaps"] = {
                "defensive_midfield": round(block_gaps.defensive_midfield_gap, 1),
                "midfield_forward": round(block_gaps.midfield_forward_gap, 1)
            }
            
            # Taktiksel uyarılar
            alerts = generate_tactical_alerts(
                tracking_points, team_id, timestamp, ball_position
            )
            
            # Uyarıları öncelik sırasına göre filtrele
            priority_alerts = filter_alerts_by_priority(alerts, max_alerts=5)
            
            analysis["alerts"] = [
                self._serialize_alert(alert) for alert in priority_alerts
            ]
            
            # Oyuncu skorları (örnek olarak ilk 3 oyuncu)
            sample_players = team_players[:3]
            for player in sample_players:
                player_scores = self._calculate_player_scores(
                    player, team_players, tracking_points
                )
                analysis["player_scores"][player.player_id] = player_scores
            
        except Exception as e:
            analysis["error"] = f"Analiz hatası: {str(e)}"
        
        return analysis
    
    def _serialize_alert(self, alert: TacticalAlert) -> Dict[str, Any]:
        """TacticalAlert'i dict'e çevirir."""
        return {
            "type": alert.alert_type.value,
            "timestamp": alert.timestamp,
            "confidence": round(alert.confidence, 2),
            "severity": alert.severity.value,
            "description": alert.description,
            "metadata": alert.metadata,
            "player_ids": alert.player_ids,
            "team_id": alert.team_id
        }
    
    def _calculate_player_scores(
        self,
        player: TrackPoint,
        team_players: List[TrackPoint],
        all_players: List[TrackPoint]
    ) -> Dict[str, float]:
        """Oyuncu skorlarını hesaplar."""
        # Basit skor hesaplama (gerçekte zaman serisi gerekli)
        player_history = [player]
        team_positions = [p for p in team_players if p.player_id != player.player_id]
        opponent_positions = [p for p in all_players if p.team_id != player.team_id]
        
        try:
            tactical_score = calculate_tactical_score(
                player_history, team_positions, opponent_positions
            )
            physical_score = calculate_physical_score(player_history)
            decision_score = calculate_decision_score(
                player_history, team_positions
            )
            
            return {
                "tactical": round(tactical_score, 1),
                "physical": round(physical_score, 1),
                "decision": round(decision_score, 1),
                "overall": round((tactical_score + physical_score + decision_score) / 3, 1)
            }
        except Exception:
            return {
                "tactical": 5.0,
                "physical": 5.0,
                "decision": 5.0,
                "overall": 5.0
            }
    
    def get_training_recommendations(
        self,
        alerts: List[Dict[str, Any]],
        team_level: str = "youth",
        session_duration: int = 90,
        player_count: int = 11
    ) -> Dict[str, Any]:
        """
        Uyarılara göre antrenman önerileri getirir.
        
        Args:
            alerts: Uyarı listesi (dict formatında)
            team_level: Takım seviyesi
            session_duration: Antrenman süresi
            player_count: Oyuncu sayısı
            
        Returns:
            Dict: Antrenman önerileri
        """
        try:
            # Dict'leri TacticalAlert'e çevir
            tactical_alerts = []
            for alert_data in alerts:
                alert = TacticalAlert(
                    alert_type=AlertType(alert_data["type"]),
                    timestamp=alert_data["timestamp"],
                    confidence=alert_data["confidence"],
                    severity=AlertSeverity(alert_data["severity"]),
                    description=alert_data["description"],
                    metadata=alert_data.get("metadata", {}),
                    player_ids=alert_data.get("player_ids"),
                    team_id=alert_data.get("team_id")
                )
                tactical_alerts.append(alert)
            
            # Antrenman seansı oluştur
            session = create_training_session(
                tactical_alerts, session_duration, team_level, player_count
            )
            
            return session
            
        except Exception as e:
            return {
                "error": f"Antrenman önerisi oluşturulamadı: {str(e)}",
                "total_duration": session_duration,
                "main_drills": []
            }
    
    def get_match_summary(
        self,
        match_id: int,
        all_alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Maç özeti oluşturur.
        
        Args:
            match_id: Maç ID'si
            all_alerts: Tüm uyarılar
            
        Returns:
            Dict: Maç özeti
        """
        try:
            # Uyarıları TacticalAlert'e çevir
            tactical_alerts = []
            for alert_data in all_alerts:
                alert = TacticalAlert(
                    alert_type=AlertType(alert_data["type"]),
                    timestamp=alert_data["timestamp"],
                    confidence=alert_data["confidence"],
                    severity=AlertSeverity(alert_data["severity"]),
                    description=alert_data["description"],
                    metadata=alert_data.get("metadata", {}),
                    player_ids=alert_data.get("player_ids"),
                    team_id=alert_data.get("team_id")
                )
                tactical_alerts.append(alert)
            
            # Özet oluştur
            summary = create_alert_summary(tactical_alerts)
            summary["match_id"] = match_id
            
            # Takım bazlı dağılım
            team_alerts = {}
            for alert in tactical_alerts:
                team_id = alert.team_id
                if team_id not in team_alerts:
                    team_alerts[team_id] = []
                team_alerts[team_id].append(alert)
            
            summary["team_breakdown"] = {}
            for team_id, alerts in team_alerts.items():
                team_summary = create_alert_summary(alerts)
                summary["team_breakdown"][team_id] = team_summary
            
            return summary
            
        except Exception as e:
            return {
                "error": f"Özet oluşturulamadı: {str(e)}",
                "match_id": match_id,
                "total_alerts": 0
            }
    
    def validate_tracking_data(self, frame_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Tracking verisini doğrular.
        
        Args:
            frame_data: Frame verisi
            
        Returns:
            Dict: Doğrulama sonucu
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "player_count": len(frame_data),
            "team_count": 0
        }
        
        if not frame_data:
            validation["valid"] = False
            validation["errors"].append("Boş veri")
            return validation
        
        required_fields = ["player_id", "team_id", "x", "y"]
        team_ids = set()
        
        for i, data in enumerate(frame_data):
            # Gerekli alanları kontrol et
            for field in required_fields:
                if field not in data:
                    validation["errors"].append(f"Oyuncu {i}: '{field}' alanı eksik")
                    validation["valid"] = False
            
            # Veri tiplerini kontrol et
            try:
                float(data.get("x", 0))
                float(data.get("y", 0))
                int(data.get("player_id", 0))
                int(data.get("team_id", 0))
            except (ValueError, TypeError):
                validation["errors"].append(f"Oyuncu {i}: Geçersiz veri tipi")
                validation["valid"] = False
            
            # Saha sınırları kontrolü
            x, y = float(data.get("x", 0)), float(data.get("y", 0))
            if not (0 <= x <= 105) or not (0 <= y <= 68):
                validation["warnings"].append(f"Oyuncu {i}: Saha dışı pozisyon ({x}, {y})")
            
            team_ids.add(data.get("team_id"))
        
        validation["team_count"] = len(team_ids)
        
        # Takım sayısı kontrolü
        if len(team_ids) > 2:
            validation["warnings"].append(f"Beklenenden fazla takım: {len(team_ids)}")
        
        return validation