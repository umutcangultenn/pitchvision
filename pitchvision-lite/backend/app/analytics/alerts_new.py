from __future__ import annotations

from collections import Counter
from typing import Any

from app.analytics.defensive_line import detect_defensive_line_break
from app.analytics.team_shape import calculate_block_gaps, calculate_team_shape
from app.analytics.types import (
    AlertSeverity,
    AlertType,
    PlayerRole,
    TacticalAlert,
    TacticalConfig,
    TrackPoint,
)


def detect_block_gap_alert(
    defensive_midfield_gap: float,
    midfield_forward_gap: float,
    team_id: int,
    timestamp: float,
) -> TacticalAlert | None:
    gap = max(defensive_midfield_gap, midfield_forward_gap)
    cfg = TacticalConfig()
    if gap <= cfg.BLOCK_GAP_WARNING_THRESHOLD:
        return None
    if gap > cfg.BLOCK_GAP_CRITICAL_THRESHOLD:
        sev = AlertSeverity.HIGH
        conf = min(1.0, (gap - cfg.BLOCK_GAP_CRITICAL_THRESHOLD) / 15.0 + 0.6)
    else:
        sev = AlertSeverity.MEDIUM
        conf = min(1.0, (gap - cfg.BLOCK_GAP_WARNING_THRESHOLD) / 20.0 + 0.45)
    return TacticalAlert(
        alert_type=AlertType.BLOCK_GAP_WIDE,
        timestamp=timestamp,
        confidence=conf,
        severity=sev,
        description="Bloklar arası mesafe yüksek.",
        metadata={"gap_m": gap},
        team_id=team_id,
    )


def detect_compactness_alert(
    compactness: float,
    team_id: int,
    timestamp: float,
) -> TacticalAlert | None:
    cfg = TacticalConfig()
    if compactness <= cfg.COMPACTNESS_WARNING_THRESHOLD:
        return None
    if compactness > cfg.COMPACTNESS_CRITICAL_THRESHOLD:
        sev = AlertSeverity.HIGH
    else:
        sev = AlertSeverity.MEDIUM
    conf = min(1.0, (compactness - cfg.COMPACTNESS_WARNING_THRESHOLD) / 25.0 + 0.4)
    return TacticalAlert(
        alert_type=AlertType.COMPACTNESS_LOST,
        timestamp=timestamp,
        confidence=conf,
        severity=sev,
        description="Takım kompaktlığı bozuldu.",
        metadata={"compactness": compactness},
        team_id=team_id,
    )


def generate_tactical_alerts(
    points: list[TrackPoint],
    team_id: int,
    timestamp: float,
) -> list[TacticalAlert]:
    if not points:
        return []
    pts = [p for p in points if p.team_id == team_id]
    if not pts:
        return []
    alerts: list[TacticalAlert] = []

    defenders = [p for p in pts if p.role == PlayerRole.DEFENDER]
    d_alert = detect_defensive_line_break(defenders, threshold_m=4.0)
    if d_alert:
        d_alert = TacticalAlert(
            alert_type=d_alert.alert_type,
            timestamp=timestamp,
            confidence=d_alert.confidence,
            severity=d_alert.severity,
            description=d_alert.description,
            metadata=d_alert.metadata,
            team_id=team_id,
        )
        alerts.append(d_alert)

    shape = calculate_team_shape(pts)
    c_alert = detect_compactness_alert(shape.compactness, team_id, timestamp)
    if c_alert:
        alerts.append(c_alert)

    gaps = calculate_block_gaps(pts)
    g_alert = detect_block_gap_alert(
        gaps.defensive_midfield_gap,
        gaps.midfield_forward_gap,
        team_id,
        timestamp,
    )
    if g_alert:
        alerts.append(g_alert)

    return alerts


_SEVERITY_ORDER: dict[AlertSeverity, int] = {
    AlertSeverity.CRITICAL: 0,
    AlertSeverity.HIGH: 1,
    AlertSeverity.MEDIUM: 2,
    AlertSeverity.LOW: 3,
}


def filter_alerts_by_priority(
    alerts: list[TacticalAlert],
    max_alerts: int = 10,
) -> list[TacticalAlert]:
    if not alerts:
        return []
    ranked = sorted(
        alerts,
        key=lambda a: (_SEVERITY_ORDER[a.severity], -a.confidence),
    )
    return ranked[:max_alerts]


def create_alert_summary(alerts: list[TacticalAlert]) -> dict[str, Any]:
    if not alerts:
        return {
            "total_alerts": 0,
            "most_frequent": None,
            "highest_priority": None,
            "by_type": {},
        }
    by_type: Counter[str] = Counter()
    for a in alerts:
        by_type[a.alert_type.value] += 1
    most_common = by_type.most_common(1)[0]
    most_frequent = {"type": most_common[0]}
    ranked = sorted(alerts, key=lambda a: (_SEVERITY_ORDER[a.severity], -a.confidence))
    hp = ranked[0]
    highest_priority = {"severity": hp.severity.value}
    return {
        "total_alerts": len(alerts),
        "most_frequent": most_frequent,
        "highest_priority": highest_priority,
        "by_type": dict(by_type),
    }
