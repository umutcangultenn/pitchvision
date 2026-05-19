"""
Module 2 — Team Color Detection.

Lightweight computer vision for approximate team distinction using
HSV color clustering. NOT full player tracking — just jersey color
grouping for team assignment.

Tolerates:
- Imperfect visibility
- Low quality video
- Unstable lighting
- Compressed recordings
"""
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try imports — graceful fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class TeamColorProfile:
    """Detected team color profile."""
    team_id: int
    dominant_hsv: Tuple[float, float, float]  # H, S, V averages
    dominant_rgb: Tuple[int, int, int]
    color_name: str  # Human-readable approximate color
    confidence: float  # 0.0-1.0
    sample_count: int  # Number of pixels/patches analyzed


@dataclass
class ColorDetectionResult:
    """Result of team color detection on a frame or set of frames."""
    team_a: Optional[TeamColorProfile]
    team_b: Optional[TeamColorProfile]
    field_color: Optional[Tuple[int, int, int]]  # Dominant field color
    detection_confidence: float
    method: str  # "hsv_kmeans", "mock"


# ── Color naming ──────────────────────────────────────────────────────────────

COLOR_RANGES_HSV = {
    "red":      ((0, 100, 100), (10, 255, 255)),
    "red2":     ((170, 100, 100), (180, 255, 255)),  # Red wraps in HSV
    "orange":   ((10, 100, 100), (25, 255, 255)),
    "yellow":   ((25, 100, 100), (35, 255, 255)),
    "green":    ((35, 100, 100), (85, 255, 255)),
    "blue":     ((85, 100, 100), (130, 255, 255)),
    "purple":   ((130, 100, 100), (160, 255, 255)),
    "pink":     ((160, 100, 100), (170, 255, 255)),
    "white":    ((0, 0, 180), (180, 30, 255)),
    "black":    ((0, 0, 0), (180, 255, 50)),
    "gray":     ((0, 0, 50), (180, 30, 180)),
}


def _name_color_hsv(h: float, s: float, v: float) -> str:
    """Approximate a human-readable color name from HSV values."""
    if v < 50:
        return "black"
    if s < 30 and v > 180:
        return "white"
    if s < 30:
        return "gray"
    # Check hue ranges
    if h < 10 or h > 170:
        return "red"
    if h < 25:
        return "orange"
    if h < 35:
        return "yellow"
    if h < 85:
        return "green"
    if h < 130:
        return "blue"
    if h < 160:
        return "purple"
    return "pink"


# ── Core detection ────────────────────────────────────────────────────────────

def extract_dominant_colors_from_bbox(
    frame: np.ndarray,
    bbox: List[int],
    n_colors: int = 3,
) -> List[Tuple[Tuple[int, int, int], float]]:
    """
    Extract dominant colors from a bounding box region.

    Uses K-means clustering on the center portion of the bbox
    (avoiding edges which often contain field/background).

    Args:
        frame: BGR image (OpenCV format).
        bbox: [x1, y1, x2, y2] bounding box.
        n_colors: Number of color clusters.

    Returns:
        List of ((R, G, B), proportion) tuples sorted by proportion.
    """
    if not CV2_AVAILABLE or not SKLEARN_AVAILABLE:
        return [((128, 128, 128), 1.0)]

    x1, y1, x2, y2 = bbox
    h, w = frame.shape[:2]

    # Clamp to frame bounds
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w, int(x2))
    y2 = min(h, int(y2))

    if x2 - x1 < 5 or y2 - y1 < 5:
        return [((128, 128, 128), 1.0)]

    # Take center 60% of bbox (torso area, more jersey visible)
    cx = (x2 - x1) // 5
    cy = (y2 - y1) // 5
    crop = frame[y1 + cy:y2 - cy, x1 + cx:x2 - cx]

    if crop.size == 0:
        return [((128, 128, 128), 1.0)]

    # Reshape to pixel list
    pixels = crop.reshape(-1, 3).astype(np.float32)

    if len(pixels) < n_colors:
        avg = pixels.mean(axis=0).astype(int)
        return [((int(avg[2]), int(avg[1]), int(avg[0])), 1.0)]

    # K-means clustering
    kmeans = KMeans(n_clusters=min(n_colors, len(pixels)), n_init=3, random_state=42)
    kmeans.fit(pixels)

    # Count cluster members
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    total = len(pixels)

    results = []
    for center, count in sorted(zip(kmeans.cluster_centers_, counts),
                                  key=lambda x: -x[1]):
        b, g, r = int(center[0]), int(center[1]), int(center[2])
        proportion = count / total
        results.append(((r, g, b), proportion))

    return results


def detect_team_colors_from_detections(
    frame: np.ndarray,
    detections: Dict[str, Any],
) -> ColorDetectionResult:
    """
    Detect team colors from player detections in a single frame.

    Args:
        frame: BGR image.
        detections: Detection dict with "players_home" and "players_away".

    Returns:
        ColorDetectionResult with team color profiles.
    """
    if not CV2_AVAILABLE or not SKLEARN_AVAILABLE:
        return _mock_color_detection()

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    team_a_colors = []
    team_b_colors = []

    # Collect dominant colors from home team bboxes
    for player in detections.get("players_home", []):
        bbox = player.get("bbox")
        if bbox:
            colors = extract_dominant_colors_from_bbox(frame, bbox, n_colors=2)
            if colors:
                team_a_colors.append(colors[0])  # Most dominant

    # Collect from away team bboxes
    for player in detections.get("players_away", []):
        bbox = player.get("bbox")
        if bbox:
            colors = extract_dominant_colors_from_bbox(frame, bbox, n_colors=2)
            if colors:
                team_b_colors.append(colors[0])

    team_a = _build_team_profile(1, team_a_colors, hsv_frame) if team_a_colors else None
    team_b = _build_team_profile(2, team_b_colors, hsv_frame) if team_b_colors else None

    # Detect field color (dominant green region)
    field_color = _detect_field_color(hsv_frame)

    # Overall confidence
    confidence = 0.0
    if team_a and team_b:
        confidence = min(team_a.confidence, team_b.confidence)
    elif team_a or team_b:
        confidence = 0.3  # Only one team detected

    return ColorDetectionResult(
        team_a=team_a,
        team_b=team_b,
        field_color=field_color,
        detection_confidence=confidence,
        method="hsv_kmeans",
    )


def _build_team_profile(
    team_id: int,
    color_samples: List[Tuple[Tuple[int, int, int], float]],
    hsv_frame: np.ndarray,
) -> TeamColorProfile:
    """Build a team color profile from collected color samples."""
    if not color_samples:
        return TeamColorProfile(
            team_id=team_id,
            dominant_hsv=(0, 0, 0),
            dominant_rgb=(128, 128, 128),
            color_name="unknown",
            confidence=0.0,
            sample_count=0,
        )

    # Average the dominant colors
    rgbs = [c[0] for c in color_samples]
    avg_r = int(np.mean([c[0] for c in rgbs]))
    avg_g = int(np.mean([c[1] for c in rgbs]))
    avg_b = int(np.mean([c[2] for c in rgbs]))

    # Convert to HSV for naming
    if CV2_AVAILABLE:
        rgb_pixel = np.uint8([[[avg_b, avg_g, avg_r]]])
        hsv_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_BGR2HSV)
        h, s, v = int(hsv_pixel[0, 0, 0]), int(hsv_pixel[0, 0, 1]), int(hsv_pixel[0, 0, 2])
    else:
        h, s, v = 0, 0, 128

    color_name = _name_color_hsv(h, s, v)

    # Confidence based on sample consistency
    if len(rgbs) >= 5:
        # Calculate color variance
        r_std = np.std([c[0] for c in rgbs])
        g_std = np.std([c[1] for c in rgbs])
        b_std = np.std([c[2] for c in rgbs])
        avg_std = (r_std + g_std + b_std) / 3
        # Lower variance = higher confidence
        confidence = max(0.3, min(0.85, 1.0 - (avg_std / 128.0)))
    else:
        confidence = 0.4

    return TeamColorProfile(
        team_id=team_id,
        dominant_hsv=(float(h), float(s), float(v)),
        dominant_rgb=(avg_r, avg_g, avg_b),
        color_name=color_name,
        confidence=round(confidence, 3),
        sample_count=len(color_samples),
    )


def _detect_field_color(hsv_frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
    """Detect the dominant field/pitch color (usually green)."""
    if not CV2_AVAILABLE:
        return (34, 139, 34)  # Default forest green

    # Green mask
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv_frame, lower_green, upper_green)

    green_pixels = hsv_frame[mask > 0]
    if len(green_pixels) > 100:
        avg_hsv = green_pixels.mean(axis=0)
        avg_pixel = np.uint8([[[int(avg_hsv[0]), int(avg_hsv[1]), int(avg_hsv[2])]]])
        bgr = cv2.cvtColor(avg_pixel, cv2.COLOR_HSV2BGR)
        return (int(bgr[0, 0, 2]), int(bgr[0, 0, 1]), int(bgr[0, 0, 0]))

    return (34, 139, 34)


def _mock_color_detection() -> ColorDetectionResult:
    """Mock color detection when CV libraries are not available."""
    return ColorDetectionResult(
        team_a=TeamColorProfile(
            team_id=1,
            dominant_hsv=(120.0, 200.0, 180.0),
            dominant_rgb=(0, 100, 200),
            color_name="blue",
            confidence=0.7,
            sample_count=11,
        ),
        team_b=TeamColorProfile(
            team_id=2,
            dominant_hsv=(0.0, 200.0, 200.0),
            dominant_rgb=(200, 50, 50),
            color_name="red",
            confidence=0.7,
            sample_count=11,
        ),
        field_color=(34, 139, 34),
        detection_confidence=0.7,
        method="mock",
    )


# ── Directional inference ─────────────────────────────────────────────────────

def infer_attacking_direction(
    team_positions: List[Tuple[float, float]],
    field_length: float,
) -> str:
    """
    Infer approximate attacking direction from team centroid position.

    If team centroid is in the left half, they're likely attacking right
    (toward the opponent's goal).

    Args:
        team_positions: List of (x, y) player positions.
        field_length: Field length in meters.

    Returns:
        "left_to_right", "right_to_left", or "uncertain".
    """
    if not team_positions or len(team_positions) < 3:
        return "uncertain"

    avg_x = np.mean([p[0] for p in team_positions])
    midfield = field_length / 2

    if avg_x < midfield * 0.8:
        return "left_to_right"
    elif avg_x > midfield * 1.2:
        return "right_to_left"
    else:
        return "uncertain"
