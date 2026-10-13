"""
Pytest fixtures — tüm test modülleri tarafından paylaşılır.
"""
import pytest
from typing import List
from app.analytics.types import TrackPoint, PlayerRole


# ── TrackPoint factory ────────────────────────────────────────────────────────

def make_point(
    player_id: int,
    team_id: int,
    role: PlayerRole,
    x: float,
    y: float,
    timestamp: float = 0.0,
    speed: float | None = None,
    vx: float | None = None,
    vy: float | None = None,
) -> TrackPoint:
    return TrackPoint(
        player_id=player_id,
        team_id=team_id,
        role=role,
        timestamp=timestamp,
        x=x,
        y=y,
        speed=speed,
        vx=vx,
        vy=vy,
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def flat_defenders() -> List[TrackPoint]:
    """Düzgün savunma hattı — 4 bek aynı x çizgisinde."""
    return [
        make_point(1, 1, PlayerRole.DEFENDER, 10.0, 15.0, 100.0),
        make_point(2, 1, PlayerRole.DEFENDER, 10.0, 25.0, 100.0),
        make_point(3, 1, PlayerRole.DEFENDER, 10.0, 40.0, 100.0),
        make_point(4, 1, PlayerRole.DEFENDER, 10.0, 55.0, 100.0),
    ]


@pytest.fixture
def broken_defenders() -> List[TrackPoint]:
    """Bozuk savunma hattı — bir bek çok ileri."""
    return [
        make_point(1, 1, PlayerRole.DEFENDER, 10.0, 15.0, 100.0),
        make_point(2, 1, PlayerRole.DEFENDER, 10.0, 25.0, 100.0),
        make_point(3, 1, PlayerRole.DEFENDER, 20.0, 40.0, 100.0),  # 10 m ileri
        make_point(4, 1, PlayerRole.DEFENDER, 10.0, 55.0, 100.0),
    ]


@pytest.fixture
def standard_team() -> List[TrackPoint]:
    """4-3-3 formasyonunda standart takım."""
    return [
        # Kaleci
        make_point(1,  1, PlayerRole.GOALKEEPER,  5.0, 34.0, 100.0),
        # Bekler
        make_point(2,  1, PlayerRole.DEFENDER,   15.0, 10.0, 100.0),
        make_point(3,  1, PlayerRole.DEFENDER,   15.0, 25.0, 100.0),
        make_point(4,  1, PlayerRole.DEFENDER,   15.0, 43.0, 100.0),
        make_point(5,  1, PlayerRole.DEFENDER,   15.0, 58.0, 100.0),
        # Orta saha
        make_point(6,  1, PlayerRole.MIDFIELDER, 35.0, 20.0, 100.0),
        make_point(7,  1, PlayerRole.MIDFIELDER, 35.0, 34.0, 100.0),
        make_point(8,  1, PlayerRole.MIDFIELDER, 35.0, 48.0, 100.0),
        # Forvetler
        make_point(9,  1, PlayerRole.FORWARD,    55.0, 15.0, 100.0),
        make_point(10, 1, PlayerRole.FORWARD,    55.0, 34.0, 100.0),
        make_point(11, 1, PlayerRole.FORWARD,    55.0, 53.0, 100.0),
    ]


@pytest.fixture
def spread_team() -> List[TrackPoint]:
    """Kompaktlığı bozulmuş takım — oyuncular çok dağınık."""
    return [
        make_point(1,  1, PlayerRole.DEFENDER,    5.0,  5.0, 100.0),
        make_point(2,  1, PlayerRole.DEFENDER,    8.0, 63.0, 100.0),
        make_point(3,  1, PlayerRole.MIDFIELDER, 50.0, 10.0, 100.0),
        make_point(4,  1, PlayerRole.MIDFIELDER, 55.0, 58.0, 100.0),
        make_point(5,  1, PlayerRole.FORWARD,    95.0, 34.0, 100.0),
    ]
