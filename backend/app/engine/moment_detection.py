"""
Module 3 — Automated Moment Detection.

Detects and suggests tactical moments from tracking data.
All detections are SUGGESTIONS — never claims certainty.
Generates EngineEvent records for analyst review.

Detected moments:
- Dangerous attacks
- Rapid transitions
- Box entries
- Pressure moments
- Attacking overloads
- Counter attacks
- Wing overloads
- Possession changes
- Defensive breakdowns
- Compactness issues
"""
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from sqlmodel import Session

from ..config import settings
from ..models.engine_event import EngineEvent, EngineEventType
from ..models.match_segment import MatchSegment
from ..engine.segmentation import assign_event_to_segment

logger = logging.getLogger(__name__)


# ── Field dimensions helper ───────────────────────────────────────────────────

def _get_field_dims() -> Tuple[float, float]:
    """Get configured field dimensions."""
    if settings.FIELD_TYPE == "hali_saha":
        return settings.HALI_SAHA_LENGTH, settings.HALI_SAHA_WIDTH
    return settings.FULL_PITCH_LENGTH, settings.FULL_PITCH_WIDTH


def _cap_confidence(raw: float) -> float:
    """Cap confidence to the configured maximum (never claim certainty)."""
    return min(raw, settings.AI_MAX_CONFIDENCE_CLAIM)


# ── Zone classification ──────────────────────────────────────────────────────

def _classify_zone_x(x: float, field_length: float) -> str:
    """Classify x-position into defensive/midfield/attacking third."""
    third = field_length / 3
    if x < third:
        return "defensive"
    elif x < 2 * third:
        return "midfield"
    return "attacking"


def _classify_zone_y(y: float, field_width: float) -> str:
    """Classify y-position into left/center/right."""
    third = field_width / 3
    if y < third:
        return "left"
    elif y < 2 * third:
        return "center"
    return "right"


# ── Core detection functions ──────────────────────────────────────────────────

def detect_dangerous_attack(
    tracking_frames: List[Dict[str, Any]],
    team_id: int,
    field_length: float,
    field_width: float,
) -> List[Dict[str, Any]]:
    """
    Detect dangerous attacks — rapid ball movement toward the goal area
    with multiple players in the attacking third.
    """
    events = []
    if len(tracking_frames) < 3:
        return events

    for i in range(2, len(tracking_frames)):
        frame = tracking_frames[i]
        prev_frame = tracking_frames[i - 2]

        ball = frame.get("ball")
        prev_ball = prev_frame.get("ball")
        if not ball or not prev_ball:
            continue

        ball_x = ball.get("position", [0, 0])[0]
        prev_ball_x = prev_ball.get("position", [0, 0])[0]

        # Ball moving toward attacking third
        attacking_threshold = field_length * 0.7
        if ball_x > attacking_threshold and prev_ball_x < attacking_threshold:
            # Count players in attacking third
            team_key = "tracks_home" if team_id == 1 else "tracks_away"
            players_in_attack = sum(
                1 for p in frame.get(team_key, [])
                if p.get("position", [0])[0] > attacking_threshold
            )

            if players_in_attack >= 3:
                confidence = _cap_confidence(
                    0.4 + min(0.3, players_in_attack * 0.05)
                )
                events.append({
                    "event_type": EngineEventType.DANGEROUS_ATTACK.value,
                    "timestamp_seconds": frame.get("timestamp", 0),
                    "confidence": confidence,
                    "description": (
                        f"Muhtemel tehlikeli atak tespit edildi — "
                        f"{players_in_attack} oyuncu hücum bölgesinde. "
                        f"Bu bir öneridir, kesinlik iddiası taşımaz."
                    ),
                    "evidence": {
                        "ball_x": ball_x,
                        "players_in_attack": players_in_attack,
                        "zone": _classify_zone_y(
                            ball.get("position", [0, 0])[1], field_width
                        ),
                        "team_id": team_id,
                    },
                })

    return events


def detect_rapid_transition(
    tracking_frames: List[Dict[str, Any]],
    team_id: int,
    field_length: float,
    field_width: float,
) -> List[Dict[str, Any]]:
    """
    Detect rapid transitions — sudden shift of team centroid
    across midfield within a short time window.
    """
    events = []
    if len(tracking_frames) < 5:
        return events

    team_key = "tracks_home" if team_id == 1 else "tracks_away"
    window_size = 5  # frames

    for i in range(window_size, len(tracking_frames)):
        current = tracking_frames[i]
        past = tracking_frames[i - window_size]

        curr_players = current.get(team_key, [])
        past_players = past.get(team_key, [])

        if len(curr_players) < 3 or len(past_players) < 3:
            continue

        curr_centroid_x = np.mean([p.get("position", [0])[0] for p in curr_players])
        past_centroid_x = np.mean([p.get("position", [0])[0] for p in past_players])

        displacement = abs(curr_centroid_x - past_centroid_x)
        midfield = field_length / 2

        # Significant displacement crossing midfield
        if displacement > field_length * 0.25:
            crossed_midfield = (
                (past_centroid_x < midfield and curr_centroid_x > midfield) or
                (past_centroid_x > midfield and curr_centroid_x < midfield)
            )
            if crossed_midfield:
                confidence = _cap_confidence(
                    0.5 + min(0.25, displacement / field_length)
                )
                events.append({
                    "event_type": EngineEventType.RAPID_TRANSITION.value,
                    "timestamp_seconds": current.get("timestamp", 0),
                    "confidence": confidence,
                    "description": (
                        f"Hızlı geçiş hareketi algılandı — "
                        f"takım ağırlık merkezi {displacement:.1f}m yer değiştirdi."
                    ),
                    "evidence": {
                        "displacement": round(displacement, 1),
                        "from_x": round(past_centroid_x, 1),
                        "to_x": round(curr_centroid_x, 1),
                        "zone": _classify_zone_y(
                            curr_centroid_x, field_width
                        ),
                        "team_id": team_id,
                    },
                })

    return events


def detect_pressure_moments(
    tracking_frames: List[Dict[str, Any]],
    team_id: int,
    field_length: float,
    field_width: float,
) -> List[Dict[str, Any]]:
    """
    Detect pressure moments — defensive clustering density
    around the ball position.
    """
    events = []
    team_key = "tracks_home" if team_id == 1 else "tracks_away"
    pressure_radius = field_length * 0.15  # Within 15% of field length

    for frame in tracking_frames:
        ball = frame.get("ball")
        if not ball:
            continue

        ball_pos = ball.get("position", [0, 0])
        players = frame.get(team_key, [])

        # Count players near the ball
        nearby = sum(
            1 for p in players
            if _distance(p.get("position", [0, 0]), ball_pos) < pressure_radius
        )

        if nearby >= 4:
            confidence = _cap_confidence(0.45 + min(0.3, nearby * 0.05))
            events.append({
                "event_type": EngineEventType.PRESSURE_MOMENT.value,
                "timestamp_seconds": frame.get("timestamp", 0),
                "confidence": confidence,
                "description": (
                    f"Baskı anı tespit edildi — {nearby} oyuncu top çevresinde. "
                    f"Yoğun savunma baskısı olabilir."
                ),
                "evidence": {
                    "nearby_players": nearby,
                    "ball_position": ball_pos,
                    "pressure_radius": round(pressure_radius, 1),
                    "zone": _classify_zone_x(ball_pos[0], field_length),
                    "team_id": team_id,
                },
            })

    return events


def detect_box_entries(
    tracking_frames: List[Dict[str, Any]],
    team_id: int,
    field_length: float,
    field_width: float,
) -> List[Dict[str, Any]]:
    """
    Detect box (penalty area) entries by the ball.
    """
    events = []
    box_x = field_length * 0.83  # Approximate penalty area start
    box_y_min = field_width * 0.2
    box_y_max = field_width * 0.8
    prev_in_box = False

    for frame in tracking_frames:
        ball = frame.get("ball")
        if not ball:
            prev_in_box = False
            continue

        bx, by = ball.get("position", [0, 0])
        in_box = bx > box_x and box_y_min < by < box_y_max

        if in_box and not prev_in_box:
            events.append({
                "event_type": EngineEventType.BOX_ENTRY.value,
                "timestamp_seconds": frame.get("timestamp", 0),
                "confidence": _cap_confidence(0.6),
                "description": "Top ceza sahasına girmiş olabilir.",
                "evidence": {
                    "ball_x": round(bx, 1),
                    "ball_y": round(by, 1),
                    "zone": _classify_zone_y(by, field_width),
                    "team_id": team_id,
                },
            })

        prev_in_box = in_box

    return events


def detect_attacking_overload(
    tracking_frames: List[Dict[str, Any]],
    team_id: int,
    opponent_team_id: int,
    field_length: float,
    field_width: float,
) -> List[Dict[str, Any]]:
    """
    Detect attacking overloads — numerical superiority in attacking zones.
    """
    events = []
    team_key = "tracks_home" if team_id == 1 else "tracks_away"
    opp_key = "tracks_home" if opponent_team_id == 1 else "tracks_away"
    attack_zone = field_length * 0.66

    for frame in tracking_frames:
        att_players = [
            p for p in frame.get(team_key, [])
            if p.get("position", [0])[0] > attack_zone
        ]
        def_players = [
            p for p in frame.get(opp_key, [])
            if p.get("position", [0])[0] > attack_zone
        ]

        advantage = len(att_players) - len(def_players)
        if advantage >= 2 and len(att_players) >= 4:
            confidence = _cap_confidence(0.45 + min(0.3, advantage * 0.1))
            events.append({
                "event_type": EngineEventType.ATTACKING_OVERLOAD.value,
                "timestamp_seconds": frame.get("timestamp", 0),
                "confidence": confidence,
                "description": (
                    f"Hücum bölgesinde sayısal üstünlük algılandı — "
                    f"{len(att_players)} vs {len(def_players)}."
                ),
                "evidence": {
                    "attackers": len(att_players),
                    "defenders": len(def_players),
                    "advantage": advantage,
                    "zone": "attacking",
                    "team_id": team_id,
                },
            })

    return events


def detect_wing_overload(
    tracking_frames: List[Dict[str, Any]],
    team_id: int,
    field_length: float,
    field_width: float,
) -> List[Dict[str, Any]]:
    """Detect wing overloads — concentration of players on flanks."""
    events = []
    team_key = "tracks_home" if team_id == 1 else "tracks_away"
    wing_threshold = field_width * 0.25

    for frame in tracking_frames:
        players = frame.get(team_key, [])
        if len(players) < 5:
            continue

        left_wing = sum(
            1 for p in players if p.get("position", [0, 0])[1] < wing_threshold
        )
        right_wing = sum(
            1 for p in players
            if p.get("position", [0, 0])[1] > field_width - wing_threshold
        )

        for wing_count, wing_name in [(left_wing, "left"), (right_wing, "right")]:
            if wing_count >= 3:
                events.append({
                    "event_type": EngineEventType.WING_OVERLOAD.value,
                    "timestamp_seconds": frame.get("timestamp", 0),
                    "confidence": _cap_confidence(0.5),
                    "description": (
                        f"{wing_name.capitalize()} kanatta yığılma tespit edildi — "
                        f"{wing_count} oyuncu."
                    ),
                    "evidence": {
                        "wing": wing_name,
                        "player_count": wing_count,
                        "zone": wing_name,
                        "team_id": team_id,
                    },
                })

    return events


def detect_compactness_issue(
    tracking_frames: List[Dict[str, Any]],
    team_id: int,
    field_length: float,
    field_width: float,
) -> List[Dict[str, Any]]:
    """Detect compactness issues — team spread too wide or too long."""
    events = []
    team_key = "tracks_home" if team_id == 1 else "tracks_away"
    max_compact_length = field_length * 0.45  # Team shouldn't span >45% of field

    for frame in tracking_frames:
        players = frame.get(team_key, [])
        if len(players) < 5:
            continue

        xs = [p.get("position", [0])[0] for p in players]
        team_length = max(xs) - min(xs)

        if team_length > max_compact_length:
            events.append({
                "event_type": EngineEventType.COMPACTNESS_ISSUE.value,
                "timestamp_seconds": frame.get("timestamp", 0),
                "confidence": _cap_confidence(0.5),
                "description": (
                    f"Takım kompaktlığı sorunu — takım uzunluğu "
                    f"{team_length:.1f}m (eşik: {max_compact_length:.1f}m)."
                ),
                "evidence": {
                    "team_length": round(team_length, 1),
                    "threshold": round(max_compact_length, 1),
                    "zone": "full_pitch",
                    "team_id": team_id,
                },
            })

    return events


# ── Utility ───────────────────────────────────────────────────────────────────

def _distance(pos1: List[float], pos2: List[float]) -> float:
    """Euclidean distance between two positions."""
    dx = pos1[0] - pos2[0]
    dy = (pos1[1] if len(pos1) > 1 else 0) - (pos2[1] if len(pos2) > 1 else 0)
    return (dx ** 2 + dy ** 2) ** 0.5


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run_moment_detection(
    tracking_frames: List[Dict[str, Any]],
    match_id: int,
    segments: List[MatchSegment],
    session: Optional[Session] = None,
) -> List[EngineEvent]:
    """
    Run all moment detection algorithms on tracking data.

    Args:
        tracking_frames: List of frame-level tracking dictionaries.
        match_id: Match ID.
        segments: List of MatchSegment records for this match.
        session: Database session (if None, events are not persisted).

    Returns:
        List of EngineEvent records (persisted if session provided).
    """
    field_length, field_width = _get_field_dims()

    all_raw_events = []

    # Run all detectors for both teams
    for team_id, opp_id in [(1, 2), (2, 1)]:
        all_raw_events.extend(
            detect_dangerous_attack(tracking_frames, team_id, field_length, field_width)
        )
        all_raw_events.extend(
            detect_rapid_transition(tracking_frames, team_id, field_length, field_width)
        )
        all_raw_events.extend(
            detect_pressure_moments(tracking_frames, team_id, field_length, field_width)
        )
        all_raw_events.extend(
            detect_box_entries(tracking_frames, team_id, field_length, field_width)
        )
        all_raw_events.extend(
            detect_attacking_overload(
                tracking_frames, team_id, opp_id, field_length, field_width
            )
        )
        all_raw_events.extend(
            detect_wing_overload(tracking_frames, team_id, field_length, field_width)
        )
        all_raw_events.extend(
            detect_compactness_issue(tracking_frames, team_id, field_length, field_width)
        )

    # Filter by confidence threshold
    threshold = settings.MOMENT_DETECTION_CONFIDENCE_THRESHOLD
    filtered = [e for e in all_raw_events if e.get("confidence", 0) >= threshold]

    # Sort by timestamp
    filtered.sort(key=lambda e: e.get("timestamp_seconds", 0))

    # Deduplicate: remove events of same type within 5 seconds
    deduped = _deduplicate_events(filtered, time_window=5.0)

    # Convert to EngineEvent models
    engine_events = []
    for raw in deduped:
        segment = assign_event_to_segment(segments, raw["timestamp_seconds"])
        event = EngineEvent(
            match_id=match_id,
            segment_id=segment.id if segment else None,
            event_type=raw["event_type"],
            timestamp_seconds=raw["timestamp_seconds"],
            confidence=raw["confidence"],
            description=raw["description"],
            evidence=raw.get("evidence"),
            created_at=datetime.utcnow(),
        )
        engine_events.append(event)

    # Persist if session provided
    if session and engine_events:
        for event in engine_events:
            session.add(event)
        session.commit()
        for event in engine_events:
            session.refresh(event)

    logger.info(
        f"Moment detection complete for match {match_id}: "
        f"{len(all_raw_events)} raw → {len(deduped)} deduplicated → "
        f"{len(engine_events)} persisted events."
    )

    return engine_events


def _deduplicate_events(
    events: List[Dict[str, Any]],
    time_window: float = 5.0,
) -> List[Dict[str, Any]]:
    """Remove events of the same type within a time window."""
    if not events:
        return []

    deduped = [events[0]]
    for event in events[1:]:
        last = deduped[-1]
        same_type = event["event_type"] == last["event_type"]
        close_time = abs(
            event["timestamp_seconds"] - last["timestamp_seconds"]
        ) < time_window
        same_team = (
            event.get("evidence", {}).get("team_id") ==
            last.get("evidence", {}).get("team_id")
        )

        if not (same_type and close_time and same_team):
            deduped.append(event)

    return deduped
