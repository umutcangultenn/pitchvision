"""
ByteTrack-based multi-object tracker via Supervision.

Design principles:
  - Tracker is initialised ONCE per video, never per frame.
  - Empty-detection frames are handled correctly (tracker ages lost tracks).
  - All outputs preserve: frame_idx, timestamp, track_id, bbox (xyxy),
    confidence, class_id, and optional pitch coordinates.
  - Team assignments are NOT set here; they come from TeamClassifier later.
  - Frame-skipping is NOT transparent to the tracker — if you skip frames,
    document the timing impact and test it explicitly.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ── Optional imports ──────────────────────────────────────────────────────────

try:
    import supervision as sv
    SV_AVAILABLE = True
    _SV_VERSION = getattr(sv, "__version__", "unknown")
    logger.info("supervision %s loaded.", _SV_VERSION)
except ImportError:
    SV_AVAILABLE = False
    logger.warning("supervision not installed — ByteTrack unavailable.")


# ── Configuration ─────────────────────────────────────────────────────────────

@dataclass
class TrackerConfig:
    """ByteTrack hyper-parameters.

    Defaults are conservative for 1080p football footage at 25 FPS.
    Tune track_activation_threshold / lost_track_buffer per camera setup.
    """
    track_activation_threshold: float = 0.25   # min conf to start a new track
    lost_track_buffer:          int   = 30     # frames before track is dropped
    minimum_matching_threshold: float = 0.8    # IoU threshold for re-matching
    frame_rate:                 int   = 25     # source video FPS (affects buffer timing)


# ── Tracked frame output ──────────────────────────────────────────────────────

def _make_tracked_frame(frame_idx: int, fps: float) -> dict[str, Any]:
    return {
        "frame_idx": frame_idx,
        "timestamp": frame_idx / fps,
        "tracks":    [],      # list of track dicts
        # Split by team AFTER TeamClassifier runs; kept empty here
        "players_home": [],
        "players_away": [],
        "ball":         None,
    }


def _track_dict(
    track_id:   int,
    bbox:       list[float],
    confidence: float,
    class_id:   int,
    pitch_xy:   tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Canonical track dict — all downstream code reads this schema."""
    x1, y1, x2, y2 = bbox
    return {
        "track_id":   int(track_id),
        "bbox":       [x1, y1, x2, y2],
        "confidence": round(float(confidence), 4),
        "class_id":   int(class_id),
        # ground-contact bottom-centre (pixel space)
        "ground_px":  [(x1 + x2) / 2.0, float(y2)],
        "center_px":  [(x1 + x2) / 2.0, (y1 + y2) / 2.0],
        # pitch coordinates — filled by homography module
        "pitch_x":    pitch_xy[0] if pitch_xy else None,
        "pitch_y":    pitch_xy[1] if pitch_xy else None,
        # team assignment — filled by TeamClassifier
        "team":       None,
    }


# ── ByteTrack wrapper ─────────────────────────────────────────────────────────

class ByteTracker:
    """Wraps ``supervision.ByteTrack`` for football footage.

    Tracker is instantiated once and updated frame-by-frame in chronological
    order.  Do NOT create a new ByteTracker for each frame.

    Args:
        config: TrackerConfig — tune for your camera FPS and resolution.
    """

    def __init__(self, config: TrackerConfig | None = None) -> None:
        if not SV_AVAILABLE:
            raise RuntimeError(
                "supervision is not installed. Run: pip install supervision"
            )
        self.config = config or TrackerConfig()
        self._tracker: Any = None
        self._fps: float = float(self.config.frame_rate)
        self._reset_tracker()

    def _reset_tracker(self) -> None:
        """(Re-)initialise the ByteTrack instance."""
        cfg = self.config
        # supervision API is stable from 0.18+; use keyword args defensively
        try:
            self._tracker = sv.ByteTrack(
                track_activation_threshold = cfg.track_activation_threshold,
                lost_track_buffer          = cfg.lost_track_buffer,
                minimum_matching_threshold = cfg.minimum_matching_threshold,
                frame_rate                 = cfg.frame_rate,
            )
        except TypeError:
            # Older supervision versions may have different param names
            logger.warning(
                "ByteTrack init with full kwargs failed — trying minimal init."
            )
            self._tracker = sv.ByteTrack()

        logger.info(
            "ByteTracker initialised (buffer=%d frames, act_thresh=%.2f).",
            cfg.lost_track_buffer, cfg.track_activation_threshold,
        )

    def set_video_fps(self, fps: float) -> None:
        """Update internal FPS used for timestamp calculation."""
        self._fps = float(fps)

    def reset(self) -> None:
        """Reset tracker state — call at the start of each new video."""
        self._reset_tracker()

    def update(
        self,
        detection_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Update tracker state with detections from one frame.

        Args:
            detection_result: Output of ``YOLODetector.detect_frame()`` or
                              ``MockDetector.detect_frame()``.

        Returns:
            Tracked frame dict with per-track bbox, ID, confidence, class_id.
        """
        frame_idx = detection_result.get("frame_idx", 0)
        tracked   = _make_tracked_frame(frame_idx, self._fps)

        raw_detections: list[dict[str, Any]] = detection_result.get("detections", [])

        if not raw_detections:
            # Pass empty Detections to keep tracker aging its lost tracks
            empty = sv.Detections.empty()
            self._tracker.update_with_detections(empty)
            return tracked

        # Build supervision Detections object
        try:
            xyxy       = np.array([d["bbox"]       for d in raw_detections], dtype=np.float32)
            confs      = np.array([d["confidence"] for d in raw_detections], dtype=np.float32)
            class_ids  = np.array([d["class_id"]   for d in raw_detections], dtype=int)

            sv_det = sv.Detections(
                xyxy        = xyxy,
                confidence  = confs,
                class_id    = class_ids,
            )
        except Exception as exc:
            logger.error("Could not build sv.Detections on frame %d: %s", frame_idx, exc)
            return tracked

        # Update ByteTrack
        try:
            sv_tracked = self._tracker.update_with_detections(sv_det)
        except Exception as exc:
            logger.error("ByteTrack update failed on frame %d: %s", frame_idx, exc)
            return tracked

        # Convert tracked detections back to our schema
        track_ids = sv_tracked.tracker_id
        if track_ids is None:
            return tracked

        tracks: list[dict[str, Any]] = []
        for i, tid in enumerate(track_ids):
            if tid is None:
                continue
            try:
                tracks.append(_track_dict(
                    track_id   = int(tid),
                    bbox       = sv_tracked.xyxy[i].tolist(),
                    confidence = float(sv_tracked.confidence[i])
                                 if sv_tracked.confidence is not None else 0.0,
                    class_id   = int(sv_tracked.class_id[i])
                                 if sv_tracked.class_id is not None else 0,
                ))
            except (IndexError, TypeError) as exc:
                logger.debug("Skipping malformed track entry %d: %s", i, exc)

        tracked["tracks"] = tracks

        logger.debug(
            "Frame %d: %d detections → %d tracks",
            frame_idx, len(raw_detections), len(tracks),
        )
        return tracked


# ── Simple IoU fallback (no supervision dependency) ──────────────────────────

class SimpleIoUTracker:
    """Minimal IoU-based tracker — used when supervision is unavailable.

    Not as robust as ByteTrack (no Kalman filter, no appearance features)
    but provides persistent IDs across frames for basic testing.
    """

    def __init__(self, iou_threshold: float = 0.3, max_lost: int = 10) -> None:
        self._iou_threshold = iou_threshold
        self._max_lost      = max_lost
        self._next_id       = 1
        self._active: dict[int, dict[str, Any]] = {}   # id → track state
        self._lost_count: dict[int, int] = {}
        self._fps: float = 25.0

    def set_video_fps(self, fps: float) -> None:
        self._fps = fps

    def reset(self) -> None:
        self._next_id    = 1
        self._active     = {}
        self._lost_count = {}

    def update(self, detection_result: dict[str, Any]) -> dict[str, Any]:
        frame_idx = detection_result.get("frame_idx", 0)
        tracked   = _make_tracked_frame(frame_idx, self._fps)
        raw_dets  = detection_result.get("detections", [])

        if not raw_dets:
            # Age all active tracks
            for tid in list(self._active.keys()):
                self._lost_count[tid] = self._lost_count.get(tid, 0) + 1
                if self._lost_count[tid] > self._max_lost:
                    del self._active[tid]
                    del self._lost_count[tid]
            return tracked

        det_bboxes = [d["bbox"] for d in raw_dets]
        assigned: dict[int, int] = {}  # det_idx → track_id

        # Greedy IoU matching
        active_ids = list(self._active.keys())
        if active_ids:
            iou_matrix = np.zeros((len(active_ids), len(det_bboxes)))
            for ti, tid in enumerate(active_ids):
                for di, dbbox in enumerate(det_bboxes):
                    iou_matrix[ti, di] = _iou(self._active[tid]["bbox"], dbbox)

            while True:
                max_val = iou_matrix.max()
                if max_val < self._iou_threshold:
                    break
                ti, di = np.unravel_index(iou_matrix.argmax(), iou_matrix.shape)
                tid = active_ids[ti]
                assigned[di] = tid
                self._active[tid]["bbox"] = det_bboxes[di]
                self._lost_count[tid] = 0
                iou_matrix[ti, :] = -1
                iou_matrix[:, di] = -1

        # Age unmatched tracks
        for ti, tid in enumerate(active_ids):
            if di not in [v for _, v in assigned.items() if _ == ti]:
                self._lost_count[tid] = self._lost_count.get(tid, 0) + 1
                if self._lost_count[tid] > self._max_lost:
                    del self._active[tid]
                    if tid in self._lost_count:
                        del self._lost_count[tid]

        # Create new tracks for unmatched detections
        for di, det in enumerate(raw_dets):
            if di not in assigned:
                new_id = self._next_id
                self._next_id += 1
                self._active[new_id] = {"bbox": det_bboxes[di]}
                self._lost_count[new_id] = 0
                assigned[di] = new_id

        tracks = []
        for di, det in enumerate(raw_dets):
            tid = assigned.get(di)
            if tid is None:
                continue
            tracks.append(_track_dict(
                track_id   = tid,
                bbox       = det_bboxes[di],
                confidence = det.get("confidence", 0.0),
                class_id   = det.get("class_id", 0),
            ))

        tracked["tracks"] = tracks
        return tracked


def _iou(a: list[float], b: list[float]) -> float:
    """Compute IoU between two [x1,y1,x2,y2] boxes."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter == 0.0:
        return 0.0
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / (area_a + area_b - inter)


# ── Factory ───────────────────────────────────────────────────────────────────

def build_tracker(config: TrackerConfig | None = None) -> ByteTracker | SimpleIoUTracker:
    """Return the best available tracker.

    Prefers ByteTrack (supervision) but falls back to SimpleIoUTracker.
    """
    cfg = config or TrackerConfig()
    if SV_AVAILABLE:
        try:
            return ByteTracker(cfg)
        except Exception as exc:
            logger.warning("ByteTracker init failed (%s) — using SimpleIoUTracker.", exc)
    logger.warning("supervision unavailable — using SimpleIoUTracker (reduced quality).")
    return SimpleIoUTracker()
