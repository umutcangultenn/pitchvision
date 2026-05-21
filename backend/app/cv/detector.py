import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from app.config import settings
import random
import logging

logger = logging.getLogger(__name__)

# Try to import OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available, using mock mode")

# Try to import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics YOLO not available")


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
    """Real YOLO detector for football player detection"""
    
    def __init__(self, model_name: str = "aabyzov/easychamp-player-detection-yolov8"):
        """
        Initialize YOLO detector with football-specific model from Hugging Face
        
        Args:
            model_name: Hugging Face model identifier
        """
        if not YOLO_AVAILABLE:
            raise RuntimeError("Ultralytics YOLO not installed. Install with: pip install ultralytics")
        
        self.model_name = model_name
        self.model = None
        self.frame_width = 1920
        self.frame_height = 1080
        
        try:
            logger.info(f"Loading YOLO model from Hugging Face: {model_name}")
            # Try to load from Hugging Face using the correct format
            # Format: https://huggingface.co/{user}/{model}/resolve/main/best.pt
            model_url = f"https://huggingface.co/{model_name}/resolve/main/best.pt"
            self.model = YOLO(model_url)
            logger.info("YOLO model loaded successfully from Hugging Face")
        except Exception as e:
            logger.warning(f"Failed to load from Hugging Face: {e}")
            logger.info("Trying to load default YOLOv8 model...")
            try:
                # Fallback to default YOLOv8 model
                self.model = YOLO("yolov8n.pt")
                logger.info("Default YOLOv8 model loaded (will download on first use)")
            except Exception as e2:
                logger.error(f"Failed to load default model: {e2}")
                logger.info("Will use mock detector as fallback")
                self.model = None
    
    def detect_frame(self, frame: np.ndarray, frame_idx: int) -> Dict[str, Any]:
        """
        Detect players, ball, and referees in a frame using YOLO
        
        Args:
            frame: Video frame (numpy array)
            frame_idx: Frame index
            
        Returns:
            Detection results with players, ball, referee positions
        """
        if self.model is None or frame is None:
            # Fallback to mock if model not available
            return self._mock_detection(frame_idx)
        
        try:
            # Run YOLO inference
            results = self.model(frame, conf=0.5, verbose=False)
            result = results[0]
            
            detections = {
                "frame_idx": frame_idx,
                "timestamp": frame_idx / 25.0,  # Assuming 25 FPS
                "players_home": [],
                "players_away": [],
                "ball": None,
                "referee": []
            }
            
            # Process detections
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Class mapping (depends on model training)
                # Typically: 0=player_home, 1=player_away, 2=ball, 3=referee
                if cls_id == 0:  # Home team player
                    detections["players_home"].append({
                        "id": len(detections["players_home"]) + 1,
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
                        "position": [(x1 + x2) / 2, (y1 + y2) / 2]
                    })
                elif cls_id == 1:  # Away team player
                    detections["players_away"].append({
                        "id": len(detections["players_away"]) + 1,
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
                        "position": [(x1 + x2) / 2, (y1 + y2) / 2]
                    })
                elif cls_id == 2:  # Ball
                    detections["ball"] = {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
                        "position": [(x1 + x2) / 2, (y1 + y2) / 2]
                    }
                elif cls_id == 3:  # Referee
                    detections["referee"].append({
                        "id": len(detections["referee"]) + 1,
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
                        "position": [(x1 + x2) / 2, (y1 + y2) / 2]
                    })
            
            logger.debug(f"Frame {frame_idx}: {len(detections['players_home'])} home, {len(detections['players_away'])} away players detected")
            return detections
            
        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
            return self._mock_detection(frame_idx)
    
    def _mock_detection(self, frame_idx: int) -> Dict[str, Any]:
        """Fallback mock detection"""
        detections = {
            "frame_idx": frame_idx,
            "timestamp": frame_idx / 25.0,
            "players_home": [],
            "players_away": [],
            "ball": None,
            "referee": []
        }
        
        for i in range(11):
            detections["players_home"].append({
                "id": i + 1,
                "bbox": [random.randint(100, 1800), random.randint(100, 1000), 
                        random.randint(100, 1800), random.randint(100, 1000)],
                "confidence": random.uniform(0.85, 0.99),
                "position": [random.randint(100, 1900), random.randint(100, 1080)]
            })
        
        for i in range(11):
            detections["players_away"].append({
                "id": i + 1,
                "bbox": [random.randint(100, 1800), random.randint(100, 1000),
                        random.randint(100, 1800), random.randint(100, 1000)],
                "confidence": random.uniform(0.85, 0.99),
                "position": [random.randint(100, 1900), random.randint(100, 1080)]
            })
        
        detections["ball"] = {
            "bbox": [random.randint(100, 1900), random.randint(100, 1080),
                    random.randint(100, 1900), random.randint(100, 1080)],
            "confidence": random.uniform(0.75, 0.95),
            "position": [random.randint(100, 1900), random.randint(100, 1080)]
        }
        
        return detections


def get_detector():
    """Factory function to get appropriate detector"""
    if settings.CV_MOCK_MODE:
        logger.info("Using MockDetector (CV_MOCK_MODE=True)")
        return MockDetector()
    else:
        logger.info("Using YOLODetector (CV_MOCK_MODE=False)")
        try:
            return YOLODetector()
        except Exception as e:
            logger.error(f"Failed to initialize YOLODetector: {e}")
            logger.info("Falling back to MockDetector")
            return MockDetector()
