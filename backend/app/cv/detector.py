"""
Player / ball detector — YOLOv8 with configurable model and device selection.

Supports:
  - YOLOv8n / YOLOv8s / YOLOv8m (configurable)
  - CPU, CUDA, Apple MPS (auto-detected or explicit)
  - FP16 inference when backend supports it
  - Graceful fallback to mock mode when YOLO is unavailable
  - Frame-level benchmarking hooks
"""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ── Optional imports (graceful fallback) ──────────────────────────────────────

try:
    import cv2  # noqa: F401
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available; mock mode only.")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics YOLO not available; falling back to mock mode.")


# ── Configuration ─────────────────────────────────────────────────────────────

@dataclass
class DetectorConfig:
    """All detection parameters in one place — pass around instead of globals."""

    # Model
    model_weights: str = "yolov8n.pt"    # path or weights name
    device: str = "auto"                 # "auto" | "cpu" | "cuda" | "mps" | "0"

    # Inference
    imgsz: int   = 960       # inference image size
    conf:  float = 0.15      # confidence threshold (lower = more detections)
    iou:   float = 0.65      # NMS IoU threshold
    max_det: int = 100       # maximum detections per frame
    half: bool   = False     # FP16 (set True only for CUDA / validated backends)

    # Class filtering
    # None = no filter (use all classes from the model)
    # [0] = COCO person class for generic yolov8*.pt weights
    # Adjust when using a football-specific model with custom classes
    classes: list[int] | None = field(default_factory=lambda: [0])

    # Frame sampling (1 = every frame; 2 = every other frame, etc.)
    frame_interval: int = 1

    # Verbose YOLO logging
    verbose: bool = False


# ── Detection output schema ───────────────────────────────────────────────────

def _make_frame_result(frame_idx: int, fps: float = 25.0) -> dict[str, Any]:
    """Empty detection result template for a single frame."""
    return {
        "frame_idx":    frame_idx,
        "timestamp":    frame_idx / fps,
        "detections":   [],      # list of detection dicts (unified, no team label yet)
        "players_home": [],      # populated after team classification
        "players_away": [],      # populated after team classification
        "ball":         None,
        "referee":      [],
    }


def _detection_dict(
    bbox: list[float],
    confidence: float,
    class_id: int,
    track_id: int | None = None,
) -> dict[str, Any]:
    """Canonical detection dict shared by all code paths."""
    x1, y1, x2, y2 = bbox
    return {
        "bbox":       [x1, y1, x2, y2],          # xyxy pixel coords
        "confidence": round(float(confidence), 4),
        "class_id":   int(class_id),
        "track_id":   track_id,
        # Convenience: bottom-centre ground contact point in pixel space
        "ground_px":  [(x1 + x2) / 2.0, float(y2)],
        "center_px":  [(x1 + x2) / 2.0, (y1 + y2) / 2.0],
    }


# ── Device helpers ────────────────────────────────────────────────────────────

def _resolve_device(requested: str) -> str:
    """Resolve 'auto' to the best available device string."""
    if requested != "auto":
        return requested

    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        # Apple Silicon MPS
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass

    return "cpu"


# ── Real YOLO detector ────────────────────────────────────────────────────────

class YOLODetector:
    """Wraps Ultralytics YOLO for football player detection.

    The model is loaded once and reused for every frame — never reinitialised
    between frames.

    Args:
        config: DetectorConfig instance.
    """

    def __init__(self, config: DetectorConfig) -> None:
        if not YOLO_AVAILABLE:
            raise RuntimeError(
                "ultralytics is not installed. Run: pip install ultralytics"
            )

        self.config = config
        self._device = _resolve_device(config.device)
        self._model: Any = None
        self._fps:   float = 25.0  # updated by caller when video FPS is known

        logger.info("Loading YOLO model: %s on %s", config.model_weights, self._device)
        self._load_model()

    def _load_model(self) -> None:
        """Load (or download) the YOLO model weights."""
        weights = self.config.model_weights
        weights_path = Path(weights)

        # If it looks like a local path and does not exist, warn but continue
        # (Ultralytics will download standard weights automatically).
        if weights_path.suffix in {".pt", ".onnx"} and not weights_path.exists():
            logger.warning(
                "Weights file not found locally: %s — Ultralytics will attempt download.",
                weights_path,
            )

        try:
            self._model = YOLO(weights)
            # Warm-up: run once on a tiny dummy image to initialise CUDA kernels
            dummy = np.zeros((32, 32, 3), dtype=np.uint8)
            self._model(dummy, device=self._device, verbose=False)
            logger.info("YOLO model ready: %s", weights)
        except Exception as exc:
            logger.error("Failed to load YOLO model %s: %s", weights, exc)
            self._model = None
            raise

    @property
    def is_available(self) -> bool:
        return self._model is not None

    def set_video_fps(self, fps: float) -> None:
        self._fps = float(fps)

    def detect_frame(
        self,
        frame: np.ndarray | None,
        frame_idx: int,
    ) -> dict[str, Any]:
        """Run inference on one frame.

        Args:
            frame: BGR image array (H×W×3). None triggers fallback to mock.
            frame_idx: Zero-based frame index.

        Returns:
            Frame detection dict (see _make_frame_result).
        """
        result = _make_frame_result(frame_idx, self._fps)

        if self._model is None or frame is None:
            logger.debug("Frame %d: model/frame unavailable — returning empty result.", frame_idx)
            return result

        if frame.ndim != 3 or frame.shape[2] != 3:
            logger.warning("Frame %d: unexpected shape %s — skipping.", frame_idx, frame.shape)
            return result

        cfg = self.config
        try:
            t0 = time.perf_counter()
            raw = self._model(
                frame,
                device  = self._device,
                imgsz   = cfg.imgsz,
                conf    = cfg.conf,
                iou     = cfg.iou,
                max_det = cfg.max_det,
                half    = cfg.half and self._device in ("cuda", "0"),
                classes = cfg.classes,
                verbose = cfg.verbose,
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000

            boxes = raw[0].boxes
            detections = []
            for box in boxes:
                det = _detection_dict(
                    bbox       = box.xyxy[0].cpu().tolist(),
                    confidence = float(box.conf[0].cpu()),
                    class_id   = int(box.cls[0].cpu()),
                )
                detections.append(det)

            result["detections"]    = detections
            result["inference_ms"]  = round(elapsed_ms, 1)

            logger.debug(
                "Frame %d: %d detections in %.1f ms",
                frame_idx, len(detections), elapsed_ms,
            )
        except Exception as exc:
            logger.error("YOLO inference error on frame %d: %s", frame_idx, exc)

        return result


# ── Mock detector (for tests / no-GPU environments) ──────────────────────────

class MockDetector:
    """Generates deterministic fake detections for testing and CI.

    NOT for production use — coordinates are random and carry no meaning.
    """

    def __init__(self, config: DetectorConfig | None = None) -> None:
        self.config   = config or DetectorConfig()
        self._fps     = 25.0
        self._rng     = random.Random(42)  # deterministic seed

    def set_video_fps(self, fps: float) -> None:
        self._fps = float(fps)

    @property
    def is_available(self) -> bool:
        return True

    def detect_frame(
        self,
        frame: np.ndarray | None,
        frame_idx: int,
    ) -> dict[str, Any]:
        result = _make_frame_result(frame_idx, self._fps)

        W = 1920 if frame is None else (frame.shape[1] if frame is not None else 1920)
        H = 1080 if frame is None else (frame.shape[0] if frame is not None else 1080)

        detections: list[dict[str, Any]] = []
        rng = self._rng

        # 22 players + 1 referee
        for _ in range(23):
            cx = rng.randint(80, W - 80)
            cy = rng.randint(80, H - 80)
            w  = rng.randint(28, 45)
            h  = rng.randint(55, 90)
            detections.append(_detection_dict(
                bbox       = [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                confidence = rng.uniform(0.55, 0.95),
                class_id   = 0,
            ))

        result["detections"] = detections
        return result


# ── Factory ───────────────────────────────────────────────────────────────────

def build_detector(config: DetectorConfig | None = None) -> YOLODetector | MockDetector:
    """Return a detector instance based on config and available dependencies.

    Tries YOLODetector first; falls back to MockDetector if YOLO is
    unavailable or the model file cannot be loaded.

    Args:
        config: DetectorConfig (uses defaults if None).

    Returns:
        A detector with a ``detect_frame(frame, frame_idx)`` interface.
    """
    cfg = config or DetectorConfig()

    if not YOLO_AVAILABLE:
        logger.warning("YOLO unavailable — using MockDetector.")
        return MockDetector(cfg)

    try:
        return YOLODetector(cfg)
    except Exception as exc:
        logger.warning("YOLODetector init failed (%s) — falling back to MockDetector.", exc)
        return MockDetector(cfg)
