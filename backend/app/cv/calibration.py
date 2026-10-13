"""
Pitch calibration module — pixel ↔ real-world coordinate transformation.

Uses Direct Linear Transform (DLT) via SVD for homography estimation.
Pure numpy implementation; no OpenCV dependency required for core math.
"""
from __future__ import annotations

import logging
import math
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# ── Low-level math ────────────────────────────────────────────────────────────

def _dlt_homography(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """Compute 3×3 perspective transform from ≥4 point correspondences (DLT).

    Args:
        src: (N, 2) pixel points.
        dst: (N, 2) real-world points (same unit as pitch coords).

    Returns:
        3×3 homography matrix H such that dst ≈ H @ src (homogeneous).
    """
    assert src.shape == dst.shape and src.shape[0] >= 4, \
        "Need at least 4 corresponding point pairs"

    A: list[list[float]] = []
    for i in range(len(src)):
        x, y = float(src[i, 0]), float(src[i, 1])
        X, Y = float(dst[i, 0]), float(dst[i, 1])
        A.append([-x, -y, -1.0,  0.0,  0.0,  0.0,  x * X,  y * X,  X])
        A.append([ 0.0,  0.0,  0.0, -x, -y, -1.0,  x * Y,  y * Y,  Y])

    _, _, Vt = np.linalg.svd(np.array(A, dtype=np.float64))
    h = Vt[-1].reshape(3, 3)

    # Normalize so h[2,2] == 1
    if abs(h[2, 2]) > 1e-12:
        h = h / h[2, 2]
    return h


def _perspective_apply(H: np.ndarray, x: float, y: float) -> tuple[float, float]:
    """Apply homography H to a single (x, y) point."""
    v = H @ np.array([x, y, 1.0], dtype=np.float64)
    if abs(v[2]) < 1e-12:
        return float(v[0]), float(v[1])
    return float(v[0] / v[2]), float(v[1] / v[2])


# ── Calibrator class ──────────────────────────────────────────────────────────

class PitchCalibrator:
    """Converts between pixel coordinates and real pitch coordinates (metres).

    Usage:
        calib = PitchCalibrator()
        calib.set_calibration_points([
            {"pixel": [px, py], "real": [rx, ry]},
            ...  # ≥ 4 points
        ])
        real_x, real_y = calib.pixel_to_real((pixel_x, pixel_y))
    """

    # Standard pitch dimensions (overridable)
    DEFAULT_PITCH_LENGTH: float = 105.0  # metres
    DEFAULT_PITCH_WIDTH: float  = 68.0   # metres

    # Fallback scale when homography is not yet calibrated
    _FALLBACK_SCALE: float = 0.05  # px → m (rough 1920×1080 assumption)

    def __init__(
        self,
        pitch_length: float = DEFAULT_PITCH_LENGTH,
        pitch_width: float  = DEFAULT_PITCH_WIDTH,
    ) -> None:
        self.pitch_length = pitch_length
        self.pitch_width  = pitch_width

        self.calibration_points: list[dict[str, Any]] = []
        self.homography_matrix:  np.ndarray | None    = None
        self._H_inv:             np.ndarray | None    = None  # cached inverse

    # ── Public API ────────────────────────────────────────────────────────────

    def set_calibration_points(self, points: list[dict[str, Any]]) -> bool:
        """Set calibration points and compute homography.

        Args:
            points: List of {"pixel": [x, y], "real": [x, y]} dicts.

        Returns:
            True if homography was computed successfully, False otherwise.
        """
        self.calibration_points = list(points)
        self.homography_matrix  = None
        self._H_inv             = None

        if len(points) < 4:
            logger.warning("Calibration requires ≥ 4 points; got %d.", len(points))
            return False

        try:
            src = np.array([p["pixel"] for p in points], dtype=np.float64)
            dst = np.array([p["real"]  for p in points], dtype=np.float64)
            self.homography_matrix = _dlt_homography(src, dst)
            self._H_inv = np.linalg.inv(self.homography_matrix)
            logger.info("Homography computed from %d calibration points.", len(points))
            return True
        except Exception as exc:
            logger.error("Homography computation failed: %s", exc)
            self.homography_matrix = None
            self._H_inv = None
            return False

    @property
    def is_calibrated(self) -> bool:
        """True when a valid homography matrix is available."""
        return self.homography_matrix is not None

    def pixel_to_real(self, pixel_xy: tuple[float, float]) -> tuple[float, float]:
        """Convert pixel (u, v) → pitch (x, y) in metres."""
        px, py = float(pixel_xy[0]), float(pixel_xy[1])
        if self.homography_matrix is None:
            return px * self._FALLBACK_SCALE, py * self._FALLBACK_SCALE
        return _perspective_apply(self.homography_matrix, px, py)

    def real_to_pixel(self, real_xy: tuple[float, float]) -> tuple[float, float]:
        """Convert pitch (x, y) in metres → pixel (u, v)."""
        rx, ry = float(real_xy[0]), float(real_xy[1])
        if self._H_inv is None:
            inv_scale = 1.0 / self._FALLBACK_SCALE
            return rx * inv_scale, ry * inv_scale
        return _perspective_apply(self._H_inv, rx, ry)

    def calculate_distance(
        self,
        pixel_a: tuple[float, float],
        pixel_b: tuple[float, float],
    ) -> float:
        """Return Euclidean distance (metres) between two pixel positions."""
        ra = self.pixel_to_real(pixel_a)
        rb = self.pixel_to_real(pixel_b)
        return math.hypot(ra[0] - rb[0], ra[1] - rb[1])

    def ground_contact(
        self,
        bbox: list[float] | tuple[float, float, float, float],
    ) -> tuple[float, float]:
        """Return pitch-coord ground-contact point from a bounding box.

        Uses the bottom-centre of the bbox as the ground contact approximation.
        This is imperfect under occlusion and large bounding-box errors but is
        the standard field-tracking convention.

        Args:
            bbox: [x1, y1, x2, y2] in pixel coordinates.

        Returns:
            (real_x, real_y) in pitch metres.
        """
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2.0
        gy = float(y2)
        return self.pixel_to_real((cx, gy))

    def is_within_pitch(
        self,
        real_xy: tuple[float, float],
        margin: float = 2.0,
    ) -> bool:
        """Return True if real-world point is inside the pitch (with margin)."""
        x, y = real_xy
        return (
            -margin <= x <= self.pitch_length + margin
            and -margin <= y <= self.pitch_width  + margin
        )

    def get_pitch_zones(self) -> dict[str, dict[str, tuple[float, float]]]:
        """Return named pitch zone boundaries in real-world coordinates."""
        L, W = self.pitch_length, self.pitch_width
        t1, t2 = L / 3.0, 2.0 * L / 3.0
        w1, w2 = W / 3.0, 2.0 * W / 3.0
        return {
            "defensive_third":  {"x": (0.0, t1), "y": (0.0, W)},
            "middle_third":     {"x": (t1, t2),  "y": (0.0, W)},
            "attacking_third":  {"x": (t2, L),   "y": (0.0, W)},
            "left_wing":        {"x": (0.0, L),  "y": (0.0, w1)},
            "center":           {"x": (0.0, L),  "y": (w1, w2)},
            "right_wing":       {"x": (0.0, L),  "y": (w2, W)},
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize calibration state for storage / API response."""
        return {
            "pitch_length":        self.pitch_length,
            "pitch_width":         self.pitch_width,
            "is_calibrated":       self.is_calibrated,
            "calibration_points":  self.calibration_points,
            "homography_matrix":   (
                self.homography_matrix.tolist()
                if self.homography_matrix is not None else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PitchCalibrator":
        """Restore a PitchCalibrator from a serialized dict."""
        calib = cls(
            pitch_length=data.get("pitch_length", cls.DEFAULT_PITCH_LENGTH),
            pitch_width =data.get("pitch_width",  cls.DEFAULT_PITCH_WIDTH),
        )
        H = data.get("homography_matrix")
        if H is not None:
            calib.homography_matrix = np.array(H, dtype=np.float64)
            calib._H_inv = np.linalg.inv(calib.homography_matrix)
        calib.calibration_points = data.get("calibration_points", [])
        return calib
