from __future__ import annotations

from app.analytics.types import (
    AlertSeverity,
    AlertType,
    DefensiveLineError,
    PlayerRole,
    TacticalAlert,
    TrackPoint,
)


def calculate_defensive_line_errors(defenders: list[TrackPoint]) -> list[DefensiveLineError]:
    defenders = [p for p in defenders if p.role == PlayerRole.DEFENDER]
    if len(defenders) < 2:
        return []
    avg_x = sum(p.x for p in defenders) / len(defenders)
    out: list[DefensiveLineError] = []
    for p in defenders:
        err = abs(p.x - avg_x)
        out.append(
            DefensiveLineError(
                line_x=avg_x,
                line_error=err,
                is_offside_trap=p.x > avg_x,
            )
        )
    return out


def detect_defensive_line_break(
    defenders: list[TrackPoint],
    threshold_m: float = 4.0,
) -> TacticalAlert | None:
    defenders = [p for p in defenders if p.role == PlayerRole.DEFENDER]
    if len(defenders) < 3:
        return None
    errors = calculate_defensive_line_errors(defenders)
    max_err = max(e.line_error for e in errors) if errors else 0.0
    if max_err <= threshold_m:
        return None
    team_id = defenders[0].team_id
    severity = AlertSeverity.HIGH if max_err >= 12.0 else AlertSeverity.MEDIUM
    confidence = min(1.0, max_err / 20.0)
    return TacticalAlert(
        alert_type=AlertType.DEFENSIVE_LINE_BREAK,
        timestamp=defenders[0].timestamp,
        confidence=confidence,
        severity=severity,
        description="Savunma hattı bozulması tespit edildi.",
        metadata={"max_line_error_m": max_err},
        team_id=team_id,
    )


def analyze_offside_trap_effectiveness(
    defenders: list[TrackPoint],
    attackers: list[TrackPoint],
) -> dict[str, float | int]:
    defenders = [p for p in defenders if p.role == PlayerRole.DEFENDER]
    attackers = [p for p in attackers if p.role == PlayerRole.FORWARD]
    if not defenders or not attackers:
        return {"offside_players": 0, "onside_players": 0, "effectiveness": 0.0}
    line_x = max(p.x for p in defenders)
    offside = sum(1 for a in attackers if a.x > line_x)
    onside = len(attackers) - offside
    effectiveness = offside / len(attackers) if attackers else 0.0
    return {
        "offside_players": offside,
        "onside_players": onside,
        "effectiveness": float(effectiveness),
    }


def calculate_defensive_line_height(defenders: list[TrackPoint]) -> dict[str, float | bool]:
    defenders = [p for p in defenders if p.role == PlayerRole.DEFENDER]
    if not defenders:
        return {"average_height": 0.0, "is_high_line": False, "is_deep_line": False}
    avg = sum(p.x for p in defenders) / len(defenders)
    return {
        "average_height": avg,
        "is_high_line": avg >= 55.0,
        "is_deep_line": avg <= 25.0,
    }
