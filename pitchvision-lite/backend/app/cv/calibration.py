from __future__ import annotations

import math
from typing import Any

import numpy as np


def _dlt_homography(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """4 nokta çiftinden 3x3 perspektif dönüşüm (DLT)."""
    A: list[list[float]] = []
    for i in range(4):
        x, y = float(src[i, 0]), float(src[i, 1])
        X, Y = float(dst[i, 0]), float(dst[i, 1])
        A.append([-x, -y, -1, 0, 0, 0, x * X, y * X, X])
        A.append([0, 0, 0, -x, -y, -1, x * Y, y * Y, Y])
    _, _, vt = np.linalg.svd(np.array(A, dtype=np.float64))
    h = vt[-1].reshape(3, 3)
    if abs(h[2, 2]) > 1e-12:
        h = h / h[2, 2]
    return h


def _perspective_apply(H: np.ndarray, x: float, y: float) -> tuple[float, float]:
    v = H @ np.array([x, y, 1.0], dtype=np.float64)
    if abs(v[2]) < 1e-12:
        return float(v[0]), float(v[1])
    return float(v[0] / v[2]), float(v[1] / v[2])


class PitchCalibrator:
    """Saha homografisi ve piksel↔metre dönüşümleri."""

    def __init__(self) -> None:
        self.pitch_length: float = 105.0
        self.pitch_width: float = 68.0
        self._pixel_scale: float = 0.05  # piksel → metre (homografi yokken)
        self.calibration_points: list[dict[str, Any]] = []
        self.homography_matrix: np.ndarray | None = None

    def set_calibration_points(self, points: list[dict[str, Any]]) -> None:
        self.calibration_points = list(points)
        self.homography_matrix = None
        if len(points) < 4:
            return
        src = np.array([p["pixel"] for p in points], dtype=np.float64)
        dst = np.array([p["real"] for p in points], dtype=np.float64)
        self.homography_matrix = _dlt_homography(src, dst)

    def pixel_to_real(self, pixel_xy: tuple[float, float]) -> tuple[float, float]:
        px, py = float(pixel_xy[0]), float(pixel_xy[1])
        if self.homography_matrix is None:
            return (px * self._pixel_scale, py * self._pixel_scale)
        return _perspective_apply(self.homography_matrix, px, py)

    def real_to_pixel(self, real_xy: tuple[float, float]) -> tuple[float, float]:
        rx, ry = float(real_xy[0]), float(real_xy[1])
        if self.homography_matrix is None:
            inv = 1.0 / self._pixel_scale
            return (rx * inv, ry * inv)
        Hinv = np.linalg.inv(self.homography_matrix)
        return _perspective_apply(Hinv, rx, ry)

    def calculate_distance(
        self,
        pixel_a: tuple[float, int] | tuple[int, int] | tuple[float, float],
        pixel_b: tuple[float, int] | tuple[int, int] | tuple[float, float],
    ) -> float:
        ra = self.pixel_to_real((float(pixel_a[0]), float(pixel_a[1])))
        rb = self.pixel_to_real((float(pixel_b[0]), float(pixel_b[1])))
        return float(math.hypot(ra[0] - rb[0], ra[1] - rb[1]))

    def get_pitch_zones(self) -> dict[str, dict[str, tuple[float, float]]]:
        L, W = self.pitch_length, self.pitch_width
        t1, t2 = L / 3, 2 * L / 3
        w1, w2 = W / 3, 2 * W / 3
        return {
            "defensive_third": {"x": (0.0, t1), "y": (0.0, W)},
            "middle_third": {"x": (t1, t2), "y": (0.0, W)},
            "attacking_third": {"x": (t2, L), "y": (0.0, W)},
            "left_wing": {"x": (0.0, L), "y": (0.0, w1)},
            "center": {"x": (0.0, L), "y": (w1, w2)},
            "right_wing": {"x": (0.0, L), "y": (w2, W)},
        }
