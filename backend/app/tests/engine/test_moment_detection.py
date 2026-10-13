import pytest
from app.engine.moment_detection import (
    detect_dangerous_attack,
    detect_box_entries,
    _classify_zone_x,
    _classify_zone_y
)

@pytest.fixture
def tracking_data():
    """Mock tracking data for testing moments."""
    return [
        {
            "timestamp": 10.0,
            "ball": {"position": [20.0, 30.0]},
            "tracks_home": [{"position": [25.0, 30.0]}, {"position": [30.0, 40.0]}],
            "tracks_away": [{"position": [35.0, 30.0]}, {"position": [40.0, 40.0]}]
        },
        {
            "timestamp": 11.0,
            "ball": {"position": [50.0, 30.0]},
            "tracks_home": [{"position": [55.0, 30.0]}, {"position": [60.0, 40.0]}],
            "tracks_away": [{"position": [45.0, 30.0]}, {"position": [50.0, 40.0]}]
        },
        {
            "timestamp": 12.0,
            "ball": {"position": [85.0, 30.0]}, # In attacking third
            "tracks_home": [
                {"position": [80.0, 30.0]}, 
                {"position": [82.0, 40.0]},
                {"position": [88.0, 20.0]}  # 3 players in attack
            ],
            "tracks_away": [{"position": [85.0, 30.0]}, {"position": [90.0, 40.0]}]
        }
    ]

def test_zone_classification():
    assert _classify_zone_x(10.0, 100.0) == "defensive"
    assert _classify_zone_x(50.0, 100.0) == "midfield"
    assert _classify_zone_x(90.0, 100.0) == "attacking"

    assert _classify_zone_y(10.0, 60.0) == "left"
    assert _classify_zone_y(30.0, 60.0) == "center"
    assert _classify_zone_y(50.0, 60.0) == "right"


def test_detect_dangerous_attack(tracking_data):
    """Test if rapid ball movement with numbers forward triggers dangerous attack."""
    events = detect_dangerous_attack(
        tracking_frames=tracking_data,
        team_id=1,
        field_length=100.0,
        field_width=60.0
    )
    
    assert len(events) == 1
    assert events[0]["event_type"] == "dangerous_attack"
    assert events[0]["timestamp_seconds"] == 12.0
    assert events[0]["evidence"]["players_in_attack"] == 3


def test_detect_box_entries(tracking_data):
    """Test box entry detection."""
    events = detect_box_entries(
        tracking_frames=tracking_data,
        team_id=1,
        field_length=100.0,
        field_width=60.0
    )
    
    # Ball enters box (x > 83) at t=12.0
    assert len(events) == 1
    assert events[0]["event_type"] == "box_entry"
    assert events[0]["timestamp_seconds"] == 12.0
    assert events[0]["evidence"]["ball_x"] == 85.0
