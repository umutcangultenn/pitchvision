import numpy as np
from typing import List, Dict, Any, Tuple
from app.config import settings
import random

# Try to import OpenCV, use mock if not available
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    # Mock cv2 module for basic functionality
    class MockCV2:
        CAP_PROP_FPS = 5
        CAP_PROP_FRAME_WIDTH = 3
        CAP_PROP_FRAME_HEIGHT = 4
        CAP_PROP_FRAME_COUNT = 7
        CAP_PROP_POS_FRAMES = 1
        
        @staticmethod
        def VideoCapture(path):
            return MockVideoCapture()
    
    class MockVideoCapture:
        def __init__(self):
            self.opened = False
        
        def isOpened(self):
            return False
        
        def get(self, prop):
            return 0
        
        def read(self):
            return False, None
        
        def release(self):
            pass
    
    cv2 = MockCV2()


class MockDetector:
    """Mock detector for demo purposes - generates realistic player positions"""
    
    def __init__(self):
        self.frame_width = 1920
        self.frame_height = 1080
        self.num_players_home = 11
        self.num_players_away = 11
        self.ball_position = [self.frame_width // 2, self.frame_height // 2]
        
    def detect_frame(self, frame: np.ndarray, frame_idx: int) -> Dict[str, Any]:
        """
        Detect players and ball in a frame
        Returns mock detection data with realistic movement
        """
        detections = {
            "frame_idx": frame_idx,
            "timestamp": frame_idx / 25.0,  # Assuming 25 FPS
            "players_home": [],
            "players_away": [],
            "ball": None,
            "referee": []
        }
        
        # Generate home team players (blue)
        for i in range(self.num_players_home):
            x = random.randint(100, self.frame_width - 100)
            y = random.randint(100, self.frame_height - 100)
            detections["players_home"].append({
                "id": i + 1,
                "bbox": [x - 20, y - 40, x + 20, y + 40],
                "confidence": random.uniform(0.85, 0.99),
                "position": [x, y]
            })
        
        # Generate away team players (red)
        for i in range(self.num_players_away):
            x = random.randint(100, self.frame_width - 100)
            y = random.randint(100, self.frame_height - 100)
            detections["players_away"].append({
                "id": i + 1,
                "bbox": [x - 20, y - 40, x + 20, y + 40],
                "confidence": random.uniform(0.85, 0.99),
                "position": [x, y]
            })
        
        # Generate ball position with some movement
        self.ball_position[0] += random.randint(-50, 50)
        self.ball_position[1] += random.randint(-50, 50)
        self.ball_position[0] = max(50, min(self.frame_width - 50, self.ball_position[0]))
        self.ball_position[1] = max(50, min(self.frame_height - 50, self.ball_position[1]))
        
        detections["ball"] = {
            "bbox": [
                self.ball_position[0] - 10,
                self.ball_position[1] - 10,
                self.ball_position[0] + 10,
                self.ball_position[1] + 10
            ],
            "confidence": random.uniform(0.75, 0.95),
            "position": self.ball_position.copy()
        }
        
        return detections


class YOLODetector:
    """Real YOLO detector - to be implemented when model is available"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        # TODO: Load YOLO model
        # self.model = YOLO(model_path)
        
    def detect_frame(self, frame: np.ndarray, frame_idx: int) -> Dict[str, Any]:
        """Detect players and ball using YOLO"""
        # TODO: Implement real YOLO detection
        raise NotImplementedError("YOLO detector not yet implemented")


def get_detector():
    """Factory function to get appropriate detector"""
    if settings.CV_MOCK_MODE:
        return MockDetector()
    else:
        return YOLODetector(settings.CV_MODEL_PATH)
