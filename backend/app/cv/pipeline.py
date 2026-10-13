"""
CV Pipeline orchestrator — ties together detector, tracker, and calibration.

Features:
  - Benchmarks detection FPS separately from end-to-end FPS
  - Processes video incrementally (no large in-memory frame buffers)
  - Reports progress via callback for API polling
  - Handles invalid videos and model errors gracefully
  - Output tracking frames are identical schema regardless of mock/real path
"""
from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from .calibration import PitchCalibrator
from .detector import DetectorConfig, build_detector
from .tracker import TrackerConfig, build_tracker

logger = logging.getLogger(__name__)

# ── Optional OpenCV ───────────────────────────────────────────────────────────
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV unavailable — cannot decode real video files.")


# ── Pipeline config ───────────────────────────────────────────────────────────

@dataclass
class PipelineConfig:
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    tracker:  TrackerConfig  = field(default_factory=TrackerConfig)

    # Frame sampling: 1=every frame, 2=every other, etc.
    frame_interval: int = 1

    # Hard cap on frames processed (0 = no limit)
    max_frames: int = 0

    # Save annotated debug video to this path (None = skip)
    output_video_path: str | None = None

    # Calibration: pass a pre-loaded PitchCalibrator or None
    calibrator: PitchCalibrator | None = None


# ── Video metadata ────────────────────────────────────────────────────────────

@dataclass
class VideoInfo:
    path: str
    fps:  float
    width: int
    height: int
    total_frames: int

    @property
    def duration_seconds(self) -> float:
        return self.total_frames / self.fps if self.fps > 0 else 0.0


def read_video_info(video_path: str) -> VideoInfo:
    """Read video metadata without decoding frames.

    Raises:
        FileNotFoundError: if the path does not exist.
        RuntimeError: if OpenCV cannot open the file.
    """
    if not CV2_AVAILABLE:
        raise RuntimeError("OpenCV is not installed; cannot read video.")

    p = Path(video_path)
    if not p.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(str(p))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open video: {video_path}")

    fps    = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    return VideoInfo(
        path=str(p), fps=fps, width=width, height=height, total_frames=total
    )


# ── Frame iterator ────────────────────────────────────────────────────────────

def iter_frames(
    video_path: str,
    frame_interval: int = 1,
    max_frames: int = 0,
) -> Iterator[tuple[int, np.ndarray]]:
    """Yield (frame_idx, bgr_frame) for each selected frame.

    Args:
        video_path:     Path to the video file.
        frame_interval: Yield every Nth frame (1 = every frame).
        max_frames:     Stop after this many DECODED frames (0 = no limit).

    Yields:
        (frame_idx, frame) tuples.
    """
    if not CV2_AVAILABLE:
        raise RuntimeError("OpenCV is required to decode video frames.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    decoded = 0
    processed = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if decoded % frame_interval == 0:
                yield decoded, frame
                processed += 1
                if max_frames > 0 and processed >= max_frames:
                    break

            decoded += 1
    finally:
        cap.release()


# ── Benchmark result ──────────────────────────────────────────────────────────

@dataclass
class BenchmarkResult:
    """Timing and detection statistics for a processed video."""
    video_path:            str
    source_fps:            float
    source_resolution:     tuple[int, int]   # (width, height)
    total_source_frames:   int
    processed_frames:      int
    total_wall_time_s:     float
    total_inference_ms:    float
    detections_total:      int

    model:      str
    device:     str
    imgsz:      int
    conf:       float
    frame_interval: int

    @property
    def inference_fps(self) -> float:
        if self.total_inference_ms <= 0:
            return 0.0
        return self.processed_frames / (self.total_inference_ms / 1000.0)

    @property
    def end_to_end_fps(self) -> float:
        if self.total_wall_time_s <= 0:
            return 0.0
        return self.processed_frames / self.total_wall_time_s

    @property
    def avg_detections_per_frame(self) -> float:
        if self.processed_frames == 0:
            return 0.0
        return self.detections_total / self.processed_frames

    def report(self) -> str:
        return (
            f"=== PitchVision Benchmark ===\n"
            f"Video        : {self.video_path}\n"
            f"Resolution   : {self.source_resolution[0]}×{self.source_resolution[1]} @ {self.source_fps:.2f} FPS\n"
            f"Source frames: {self.total_source_frames}  (processed: {self.processed_frames}, interval: {self.frame_interval})\n"
            f"Model        : {self.model}  |  device: {self.device}  |  imgsz: {self.imgsz}  |  conf: {self.conf}\n"
            f"Wall time    : {self.total_wall_time_s:.2f}s\n"
            f"Inference FPS: {self.inference_fps:.1f}  (model only)\n"
            f"E2E FPS      : {self.end_to_end_fps:.1f}  (decode + infer + track)\n"
            f"Detections   : {self.detections_total} total  ({self.avg_detections_per_frame:.1f} avg/frame)\n"
        )


# ── Main pipeline ─────────────────────────────────────────────────────────────

class CVPipeline:
    """End-to-end CV pipeline: video → tracked frames with pitch coords.

    Usage:
        pipeline = CVPipeline(config)
        frames   = list(pipeline.process(video_path, on_progress=cb))
    """

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config   = config or PipelineConfig()
        self.detector = build_detector(self.config.detector)
        self.tracker  = build_tracker(self.config.tracker)
        self.calibrator = self.config.calibrator or PitchCalibrator()

    def process(
        self,
        video_path: str,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> list[dict[str, Any]]:
        """Process a video file and return tracked frames.

        Args:
            video_path:  Path to the video.
            on_progress: Optional ``(processed, total)`` callback for progress.

        Returns:
            List of tracked-frame dicts (see tracker._make_tracked_frame).
        """
        cfg = self.config

        # ── Video metadata ────────────────────────────────────────────────────
        try:
            info = read_video_info(video_path)
        except (FileNotFoundError, RuntimeError) as exc:
            logger.error("Pipeline: video error — %s", exc)
            return self._run_mock_fallback()

        self.detector.set_video_fps(info.fps)
        self.tracker.set_video_fps(info.fps)
        self.tracker.reset()

        logger.info(
            "Pipeline: %s — %.0f FPS, %dx%d, %d frames",
            video_path, info.fps, info.width, info.height, info.total_frames,
        )

        tracking_frames: list[dict[str, Any]] = []
        processed = 0

        try:
            for frame_idx, frame in iter_frames(
                video_path,
                frame_interval=cfg.frame_interval,
                max_frames=cfg.max_frames,
            ):
                # Detect
                det_result  = self.detector.detect_frame(frame, frame_idx)
                # Track
                tracked     = self.tracker.update(det_result)
                # Apply homography
                tracked     = self._apply_homography(tracked)

                tracking_frames.append(tracked)
                processed += 1

                if on_progress and processed % 25 == 0:
                    on_progress(processed, info.total_frames)

                if processed % 100 == 0:
                    logger.info("Pipeline: processed %d / ~%d frames", processed, info.total_frames)

        except Exception as exc:
            logger.error("Pipeline: error during processing — %s", exc, exc_info=True)

        logger.info("Pipeline: done — %d tracking frames.", len(tracking_frames))
        return tracking_frames

    def benchmark(
        self,
        video_path: str,
        max_frames: int = 300,
    ) -> BenchmarkResult:
        """Run detection + tracking on up to max_frames and return timing stats.

        Use this on a short clip before processing a full match.
        """
        try:
            info = read_video_info(video_path)
        except (FileNotFoundError, RuntimeError) as exc:
            raise RuntimeError(f"Benchmark: cannot read video — {exc}") from exc

        self.detector.set_video_fps(info.fps)
        self.tracker.set_video_fps(info.fps)
        self.tracker.reset()

        cfg = self.config
        total_inference_ms = 0.0
        detections_total   = 0
        processed          = 0

        wall_start = time.perf_counter()

        for frame_idx, frame in iter_frames(
            video_path,
            frame_interval=cfg.frame_interval,
            max_frames=max_frames,
        ):
            det = self.detector.detect_frame(frame, frame_idx)
            total_inference_ms += det.get("inference_ms", 0.0)
            detections_total   += len(det.get("detections", []))
            self.tracker.update(det)
            processed += 1

        wall_time = time.perf_counter() - wall_start

        det_cfg = cfg.detector
        return BenchmarkResult(
            video_path           = video_path,
            source_fps           = info.fps,
            source_resolution    = (info.width, info.height),
            total_source_frames  = info.total_frames,
            processed_frames     = processed,
            total_wall_time_s    = wall_time,
            total_inference_ms   = total_inference_ms,
            detections_total     = detections_total,
            model                = det_cfg.model_weights,
            device               = det_cfg.device,
            imgsz                = det_cfg.imgsz,
            conf                 = det_cfg.conf,
            frame_interval       = cfg.frame_interval,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _apply_homography(self, tracked: dict[str, Any]) -> dict[str, Any]:
        """Enrich each track with pitch-coordinate ground contact point."""
        if not self.calibrator.is_calibrated:
            return tracked

        for t in tracked.get("tracks", []):
            bbox = t.get("bbox")
            if bbox:
                try:
                    rx, ry = self.calibrator.ground_contact(bbox)
                    if self.calibrator.is_within_pitch((rx, ry)):
                        t["pitch_x"] = round(rx, 2)
                        t["pitch_y"] = round(ry, 2)
                    else:
                        t["pitch_x"] = None
                        t["pitch_y"] = None
                except Exception:
                    pass  # leave pitch_x/y as None

        return tracked

    def _run_mock_fallback(self) -> list[dict[str, Any]]:
        """Generate 150 mock frames when video cannot be opened."""
        logger.warning("Pipeline: running mock fallback (150 synthetic frames).")
        from .detector import MockDetector
        mock = MockDetector(self.config.detector)
        self.tracker.reset()
        frames = []
        for i in range(150):
            det     = mock.detect_frame(None, i)
            tracked = self.tracker.update(det)
            frames.append(tracked)
        return frames
