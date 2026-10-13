from __future__ import annotations

import math
from typing import Iterable

from app.analytics.types import BlockGaps, PlayerRole, TacticalConfig, TeamShape, TrackPoint


def calculate_team_shape(points: list[TrackPoint]) -> TeamShape:
    if not points:
        raise ValueError("points must not be empty")
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    team_length = max(xs) - min(xs)
    team_width = max(ys) - min(ys)
    n = len(points)
    centroid_x = sum(xs) / n
    centroid_y = sum(ys) / n
    if n == 1:
        compactness = 0.0
    else:
        dists = [math.hypot(p.x - centroid_x, p.y - centroid_y) for p in points]
        compactness = sum(dists) / n
    return TeamShape(
        team_length=team_length,
        team_width=team_width,
        centroid_x=centroid_x,
        centroid_y=centroid_y,
        compactness=compactness,
    )


def _avg_x(pts: Iterable[TrackPoint]) -> float:
    pts = list(pts)
    if not pts:
        return 0.0
    return sum(p.x for p in pts) / len(pts)


def calculate_block_gaps(points: list[TrackPoint]) -> BlockGaps:
    defenders = [p for p in points if p.role == PlayerRole.DEFENDER]
    mids = [p for p in points if p.role == PlayerRole.MIDFIELDER]
    fwds = [p for p in points if p.role == PlayerRole.FORWARD]

    def_mid = 0.0
    if defenders and mids:
        def_mid = abs(_avg_x(mids) - _avg_x(defenders))
    mid_fwd = 0.0
    if mids and fwds:
        mid_fwd = abs(_avg_x(fwds) - _avg_x(mids))
    return BlockGaps(defensive_midfield_gap=def_mid, midfield_forward_gap=mid_fwd)


def calculate_team_width_by_thirds(points: list[TrackPoint]) -> dict[str, float]:
    if not points:
        return {"defensive_third": 0.0, "middle_third": 0.0, "attacking_third": 0.0}
    L = TacticalConfig.FIELD_LENGTH
    w1, w2 = L / 3, 2 * L / 3

    def width_of(sub: list[TrackPoint]) -> float:
        if len(sub) < 2:
            return 0.0
        ys = [p.y for p in sub]
        return max(ys) - min(ys)

    d_third = [p for p in points if p.x < w1]
    m_third = [p for p in points if w1 <= p.x < w2]
    a_third = [p for p in points if p.x >= w2]
    return {
        "defensive_third": width_of(d_third),
        "middle_third": width_of(m_third),
        "attacking_third": width_of(a_third),
    }


def _group_compactness(pts: list[TrackPoint]) -> float:
    if len(pts) < 2:
        return 0.0
    dists: list[float] = []
    for i, a in enumerate(pts):
        for b in pts[i + 1 :]:
            dists.append(math.hypot(a.x - b.x, a.y - b.y))
    return sum(dists) / len(dists)


def calculate_formation_compactness(points: list[TrackPoint]) -> dict[str, float]:
    defenders = [p for p in points if p.role == PlayerRole.DEFENDER]
    mids = [p for p in points if p.role == PlayerRole.MIDFIELDER]
    fwds = [p for p in points if p.role == PlayerRole.FORWARD]
    return {
        "defenders": _group_compactness(defenders),
        "midfielders": _group_compactness(mids),
        "forwards": _group_compactness(fwds),
    }
