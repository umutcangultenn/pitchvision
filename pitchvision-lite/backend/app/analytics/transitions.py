from __future__ import annotations

from app.analytics.types import (
    AlertSeverity,
    AlertType,
    TacticalAlert,
    TacticalConfig,
    TrackPoint,
    TransitionMetrics,
)


def calculate_transition_speed(start_x: float, end_x: float, seconds: float) -> float:
    if seconds <= 0:
        return 0.0
    return abs(end_x - start_x) / seconds


def analyze_team_transition(
    start_positions: list[TrackPoint],
    end_positions: list[TrackPoint],
    direction: str,
) -> TransitionMetrics:
    if not start_positions or not end_positions:
        return TransitionMetrics(
            start_x=0.0,
            end_x=0.0,
            duration=0.0,
            speed=0.0,
            player_count=0,
            success=False,
        )
    sx = sum(p.x for p in start_positions) / len(start_positions)
    ex = sum(p.x for p in end_positions) / len(end_positions)
    t0 = min(p.timestamp for p in start_positions)
    t1 = max(p.timestamp for p in end_positions)
    duration = max(t1 - t0, 1e-6)
    speed = abs(ex - sx) / duration
    thr = TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD
    success = direction == "attack" and (ex > sx) and speed >= thr
    return TransitionMetrics(
        start_x=sx,
        end_x=ex,
        duration=t1 - t0,
        speed=speed,
        player_count=len(start_positions),
        success=success,
    )


def detect_slow_transition_alert(
    players: list[TrackPoint],
    ball_xy: tuple[float, float],
    timestamp: float,
) -> TacticalAlert | None:
    if len(players) < 4:
        return None
    bx, by = ball_xy
    slow = 0
    for p in players:
        sp = p.speed if p.speed is not None else 0.0
        if sp < 2.5:
            slow += 1
    if slow < 5:
        return None
    team_id = players[0].team_id
    return TacticalAlert(
        alert_type=AlertType.TRANSITION_SLOW,
        timestamp=timestamp,
        confidence=0.75,
        severity=AlertSeverity.MEDIUM,
        description="Yavaş geçiş.",
        metadata={"slow_players": slow},
        team_id=team_id,
    )


def detect_slow_transition_alert_detailed(
    metrics: TransitionMetrics,
    team_id: int,
    timestamp: float,
) -> TacticalAlert | None:
    thr = TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD
    if metrics.speed >= thr:
        return None
    if metrics.speed < 1.0:
        sev = AlertSeverity.HIGH
    else:
        sev = AlertSeverity.MEDIUM
    conf = max(0.1, min(1.0, 1.0 - metrics.speed / thr))
    return TacticalAlert(
        alert_type=AlertType.TRANSITION_SLOW,
        timestamp=timestamp,
        confidence=conf,
        severity=sev,
        description="Geçiş hızı düşük.",
        metadata={"speed_m_s": metrics.speed},
        team_id=team_id,
    )
