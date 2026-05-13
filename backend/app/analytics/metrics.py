from typing import Dict, Any, List
import numpy as np
from collections import defaultdict


class TacticalMetricsCalculator:
    """Calculate tactical metrics from tracking data"""
    
    def __init__(self, tracking_data: List[Dict[str, Any]]):
        self.tracking_data = tracking_data
        self.fps = 25.0
        
    def calculate_possession(self) -> Dict[str, float]:
        """Calculate possession percentage"""
        home_possession_frames = 0
        away_possession_frames = 0
        total_frames = len(self.tracking_data)
        
        for frame in self.tracking_data:
            if not frame.get("ball"):
                continue
            
            ball_pos = frame["ball"]["position"]
            
            # Find closest player to ball
            min_dist_home = float('inf')
            min_dist_away = float('inf')
            
            for player in frame.get("tracks_home", []):
                dist = self._distance(ball_pos, player["position"])
                min_dist_home = min(min_dist_home, dist)
            
            for player in frame.get("tracks_away", []):
                dist = self._distance(ball_pos, player["position"])
                min_dist_away = min(min_dist_away, dist)
            
            if min_dist_home < min_dist_away:
                home_possession_frames += 1
            else:
                away_possession_frames += 1
        
        total_possession = home_possession_frames + away_possession_frames
        if total_possession == 0:
            return {"home": 50.0, "away": 50.0}
        
        return {
            "home": (home_possession_frames / total_possession) * 100,
            "away": (away_possession_frames / total_possession) * 100
        }
    
    def calculate_distance_covered(self) -> Dict[str, Dict[int, float]]:
        """Calculate distance covered by each player (in km)"""
        distances = {"home": defaultdict(float), "away": defaultdict(float)}
        
        prev_positions_home = {}
        prev_positions_away = {}
        
        for frame in self.tracking_data:
            # Home team
            for player in frame.get("tracks_home", []):
                track_id = player["track_id"]
                pos = player["position"]
                
                if track_id in prev_positions_home:
                    dist = self._distance(pos, prev_positions_home[track_id])
                    # Convert pixels to meters (mock conversion)
                    distances["home"][track_id] += dist * 0.05 / 1000  # to km
                
                prev_positions_home[track_id] = pos
            
            # Away team
            for player in frame.get("tracks_away", []):
                track_id = player["track_id"]
                pos = player["position"]
                
                if track_id in prev_positions_away:
                    dist = self._distance(pos, prev_positions_away[track_id])
                    distances["away"][track_id] += dist * 0.05 / 1000  # to km
                
                prev_positions_away[track_id] = pos
        
        return {
            "home": dict(distances["home"]),
            "away": dict(distances["away"])
        }
    
    def calculate_heatmaps(self) -> Dict[str, Dict[int, List]]:
        """Calculate heatmap data for each player"""
        heatmaps = {"home": defaultdict(list), "away": defaultdict(list)}
        
        for frame in self.tracking_data:
            for player in frame.get("tracks_home", []):
                track_id = player["track_id"]
                heatmaps["home"][track_id].append(player["position"])
            
            for player in frame.get("tracks_away", []):
                track_id = player["track_id"]
                heatmaps["away"][track_id].append(player["position"])
        
        return {
            "home": dict(heatmaps["home"]),
            "away": dict(heatmaps["away"])
        }
    
    def calculate_passes(self) -> Dict[str, int]:
        """Estimate pass counts (simplified)"""
        # In real implementation, detect pass events from ball movement
        return {
            "home_completed": np.random.randint(200, 400),
            "home_attempted": np.random.randint(250, 450),
            "away_completed": np.random.randint(180, 380),
            "away_attempted": np.random.randint(230, 430)
        }
    
    def calculate_shots(self) -> Dict[str, int]:
        """Estimate shot counts"""
        return {
            "home": np.random.randint(8, 20),
            "away": np.random.randint(6, 18)
        }
    
    def _distance(self, pos1: List[float], pos2: List[float]) -> float:
        """Calculate Euclidean distance"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Calculate all metrics"""
        return {
            "possession": self.calculate_possession(),
            "distance_covered": self.calculate_distance_covered(),
            "heatmaps": self.calculate_heatmaps(),
            "passes": self.calculate_passes(),
            "shots": self.calculate_shots()
        }
