import numpy as np
from typing import Dict, Any, List, Tuple


class PitchCalibrator:
    """
    Pitch calibration for converting pixel coordinates to real-world coordinates
    Standard football pitch: 105m x 68m
    """
    
    def __init__(self):
        self.pitch_length = 105.0  # meters
        self.pitch_width = 68.0    # meters
        self.calibration_points = []
        self.homography_matrix = None
        
    def set_calibration_points(self, points: List[Dict[str, Any]]):
        """
        Set calibration points from user input
        Each point should have: {"pixel": [x, y], "real": [x, y]}
        """
        self.calibration_points = points
        if len(points) >= 4:
            self._compute_homography()
    
    def _compute_homography(self):
        """Compute homography matrix from calibration points"""
        if len(self.calibration_points) < 4:
            return
        
        pixel_points = np.array([p["pixel"] for p in self.calibration_points], dtype=np.float32)
        real_points = np.array([p["real"] for p in self.calibration_points], dtype=np.float32)
        
        # In real implementation, use cv2.findHomography
        # For now, create identity matrix
        self.homography_matrix = np.eye(3)
    
    def pixel_to_real(self, pixel_coords: Tuple[float, float]) -> Tuple[float, float]:
        """Convert pixel coordinates to real-world coordinates"""
        if self.homography_matrix is None:
            # Return mock conversion
            return (pixel_coords[0] * 0.05, pixel_coords[1] * 0.05)
        
        # TODO: Apply homography transformation
        return (pixel_coords[0] * 0.05, pixel_coords[1] * 0.05)
    
    def real_to_pixel(self, real_coords: Tuple[float, float]) -> Tuple[float, float]:
        """Convert real-world coordinates to pixel coordinates"""
        if self.homography_matrix is None:
            return (real_coords[0] * 20, real_coords[1] * 20)
        
        # TODO: Apply inverse homography
        return (real_coords[0] * 20, real_coords[1] * 20)
    
    def calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate real-world distance between two positions"""
        real1 = self.pixel_to_real(pos1)
        real2 = self.pixel_to_real(pos2)
        
        dx = real2[0] - real1[0]
        dy = real2[1] - real1[1]
        
        return np.sqrt(dx**2 + dy**2)
    
    def get_pitch_zones(self) -> Dict[str, Any]:
        """Get pitch zone definitions"""
        return {
            "defensive_third": {"x": [0, 35], "y": [0, 68]},
            "middle_third": {"x": [35, 70], "y": [0, 68]},
            "attacking_third": {"x": [70, 105], "y": [0, 68]},
            "left_wing": {"x": [0, 105], "y": [0, 22.67]},
            "center": {"x": [0, 105], "y": [22.67, 45.33]},
            "right_wing": {"x": [0, 105], "y": [45.33, 68]}
        }
