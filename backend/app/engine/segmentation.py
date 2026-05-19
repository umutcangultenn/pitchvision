"""
Module 1 — Match Segmentation.

Splits a match into time-based segments and calculates per-segment
tactical metrics. Adapts to match duration (halı saha vs full pitch).
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from sqlmodel import Session, select

from ..config import settings
from ..models.match_segment import MatchSegment, SegmentLabel
from ..models.match import Match

logger = logging.getLogger(__name__)


# ── Segment definitions ──────────────────────────────────────────────────────

SEGMENTS_90MIN = [
    {"label": "0-15",     "start": 0,    "end": 900},
    {"label": "15-30",    "start": 900,  "end": 1800},
    {"label": "30-45",    "start": 1800, "end": 2700},
    {"label": "halftime", "start": 2700, "end": 2700},  # marker only
    {"label": "45-60",    "start": 2700, "end": 3600},
    {"label": "60-75",    "start": 3600, "end": 4500},
    {"label": "75-90",    "start": 4500, "end": 5400},
]

SEGMENTS_60MIN = [
    {"label": "0-10",          "start": 0,    "end": 600},
    {"label": "10-20",         "start": 600,  "end": 1200},
    {"label": "20-30",         "start": 1200, "end": 1800},
    {"label": "halftime-short","start": 1800, "end": 1800},
    {"label": "30-40",         "start": 1800, "end": 2400},
    {"label": "40-50",         "start": 2400, "end": 3000},
    {"label": "50-60",         "start": 3000, "end": 3600},
]


def get_segment_definitions(duration_minutes: int) -> List[Dict[str, Any]]:
    """
    Get segment definitions adapted to the match duration.

    Args:
        duration_minutes: Total match duration in minutes.

    Returns:
        List of segment definitions with label, start, end (in seconds).
    """
    if duration_minutes <= 70:
        # Halı saha / short match — use 10-minute segments
        return SEGMENTS_60MIN
    else:
        # Full pitch — use 15-minute segments
        return SEGMENTS_90MIN


def generate_segments_for_match(
    session: Session,
    match_id: int,
    duration_minutes: Optional[int] = None,
) -> List[MatchSegment]:
    """
    Generate time-based segments for a match and persist them.

    If segments already exist for this match, they are returned as-is.

    Args:
        session: Database session.
        match_id: Match ID.
        duration_minutes: Override match duration (auto-detected if None).

    Returns:
        List of created/existing MatchSegment records.
    """
    # Check if segments already exist
    existing = session.exec(
        select(MatchSegment).where(MatchSegment.match_id == match_id)
    ).all()
    if existing:
        logger.info(f"Match {match_id} already has {len(existing)} segments.")
        return list(existing)

    # Get match to determine duration
    match = session.get(Match, match_id)
    if not match:
        logger.error(f"Match {match_id} not found.")
        return []

    duration = duration_minutes or match.duration_minutes or 90
    segment_defs = get_segment_definitions(duration)

    segments = []
    for seg_def in segment_defs:
        segment = MatchSegment(
            match_id=match_id,
            segment_label=seg_def["label"],
            start_time=float(seg_def["start"]),
            end_time=float(seg_def["end"]),
            event_density=0.0,
            transition_count=0,
            dangerous_attacks=0,
            box_entries=0,
            analysis_confidence=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(segment)
        segments.append(segment)

    session.commit()
    # Refresh to get IDs
    for seg in segments:
        session.refresh(seg)

    logger.info(
        f"Created {len(segments)} segments for match {match_id} "
        f"(duration={duration}min)."
    )
    return segments


def assign_event_to_segment(
    segments: List[MatchSegment],
    timestamp_seconds: float,
) -> Optional[MatchSegment]:
    """
    Find which segment a timestamp belongs to.

    Args:
        segments: List of match segments.
        timestamp_seconds: Event timestamp in seconds.

    Returns:
        The matching MatchSegment, or None if no match.
    """
    for seg in segments:
        # Skip halftime markers
        if "halftime" in seg.segment_label:
            continue
        if seg.start_time <= timestamp_seconds < seg.end_time:
            return seg
    return None


def update_segment_metrics(
    session: Session,
    segment: MatchSegment,
    engine_events: List[Dict[str, Any]],
) -> MatchSegment:
    """
    Recalculate segment-level metrics from engine events within this segment.

    Args:
        session: Database session.
        segment: The segment to update.
        engine_events: List of engine event dicts within this segment's time range.

    Returns:
        Updated MatchSegment.
    """
    if not engine_events:
        return segment

    duration_minutes = (segment.end_time - segment.start_time) / 60.0
    if duration_minutes <= 0:
        return segment

    # Event density = events per minute
    segment.event_density = len(engine_events) / duration_minutes

    # Count specific event types
    segment.dangerous_attacks = sum(
        1 for e in engine_events
        if e.get("event_type") in ("dangerous_attack", "counter_attack")
    )
    segment.transition_count = sum(
        1 for e in engine_events
        if e.get("event_type") in ("rapid_transition", "transition_burst")
    )
    segment.box_entries = sum(
        1 for e in engine_events
        if e.get("event_type") == "box_entry"
    )

    # Attack tendency — left / center / right distribution
    attack_events = [
        e for e in engine_events
        if e.get("event_type") in (
            "dangerous_attack", "counter_attack", "wing_overload", "box_entry"
        )
    ]
    if attack_events:
        left = sum(1 for e in attack_events if e.get("evidence", {}).get("zone") == "left")
        right = sum(1 for e in attack_events if e.get("evidence", {}).get("zone") == "right")
        center = len(attack_events) - left - right
        total = len(attack_events)
        segment.attack_tendency = {
            "left": round(left / total, 2),
            "center": round(center / total, 2),
            "right": round(right / total, 2),
        }

    # Pressure tendency
    pressure_events = [
        e for e in engine_events
        if e.get("event_type") in ("pressure_moment", "pressing_moment")
    ]
    segment.pressure_tendency = {
        "pressure_events": len(pressure_events),
        "pressure_density": round(
            len(pressure_events) / duration_minutes, 2
        ) if duration_minutes > 0 else 0,
    }

    # Average confidence of events in segment
    confidences = [e.get("confidence", 0.0) for e in engine_events]
    segment.analysis_confidence = round(
        sum(confidences) / len(confidences), 3
    ) if confidences else 0.0

    segment.updated_at = datetime.utcnow()
    session.add(segment)
    session.commit()
    session.refresh(segment)

    return segment
