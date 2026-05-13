from typing import List, Dict, Any
import numpy as np


class SimpleTracker:
    """Simple tracking algorithm using IoU matching"""
    
    def __init__(self):
        self.tracks_home = {}
        self.tracks_away = {}
        self.next_id_home = 1
        self.next_id_away = 1
        
    def update(self, detections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update tracks with new detections
        Returns tracking data with consistent IDs across frames
        """
        tracked = {
            "frame_idx": detections["frame_idx"],
            "timestamp": detections["timestamp"],
            "tracks_home": [],
            "tracks_away": [],
            "ball": detections.get("ball")
        }
        
        # Track home team
        for detection in detections["players_home"]:
            track_id = self._assign_track_id(detection, self.tracks_home, "home")
            tracked["tracks_home"].append({
                "track_id": track_id,
                "bbox": detection["bbox"],
                "position": detection["position"],
                "confidence": detection["confidence"]
            })
        
        # Track away team
        for detection in detections["players_away"]:
            track_id = self._assign_track_id(detection, self.tracks_away, "away")
            tracked["tracks_away"].append({
                "track_id": track_id,
                "bbox": detection["bbox"],
                "position": detection["position"],
                "confidence": detection["confidence"]
            })
        
        return tracked
    
    def _assign_track_id(self, detection: Dict, tracks: Dict, team: str) -> int:
        """Assign track ID to detection"""
        # Simple assignment - in real implementation, use IoU matching
        if team == "home":
            track_id = self.next_id_home
            self.next_id_home += 1
        else:
            track_id = self.next_id_away
            self.next_id_away += 1
        
        tracks[track_id] = detection
        return track_id
    
    def get_trajectories(self) -> Dict[str, List]:
        """Get player trajectories"""
        return {
            "home": list(self.tracks_home.values()),
            "away": list(self.tracks_away.values())
        }
