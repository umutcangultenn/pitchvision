import pytest
from app.engine.segmentation import get_segment_definitions, assign_event_to_segment
from app.models.match_segment import MatchSegment


def test_segment_definitions_90_min():
    """Test segmentation definition for full 90-minute match."""
    defs = get_segment_definitions(90)
    assert len(defs) == 7
    # 0-15, 15-30, 30-45, halftime, 45-60, 60-75, 75-90
    assert defs[0]["label"] == "0-15"
    assert defs[-1]["label"] == "75-90"
    assert defs[0]["end"] == 900
    assert defs[-1]["end"] == 5400


def test_segment_definitions_60_min():
    """Test segmentation definition for halı saha 60-minute match."""
    defs = get_segment_definitions(60)
    assert len(defs) == 7
    # 0-10, 10-20, 20-30, halftime-short, 30-40, 40-50, 50-60
    assert defs[0]["label"] == "0-10"
    assert defs[-1]["label"] == "50-60"
    assert defs[0]["end"] == 600
    assert defs[-1]["end"] == 3600


def test_assign_event_to_segment():
    """Test assigning an event timestamp to the correct segment."""
    segments = [
        MatchSegment(id=1, match_id=1, segment_label="0-15", start_time=0, end_time=900),
        MatchSegment(id=2, match_id=1, segment_label="15-30", start_time=900, end_time=1800),
        MatchSegment(id=3, match_id=1, segment_label="halftime", start_time=1800, end_time=1800),
        MatchSegment(id=4, match_id=1, segment_label="30-45", start_time=1800, end_time=2700),
    ]

    # At 5 mins -> 0-15
    seg1 = assign_event_to_segment(segments, 300)
    assert seg1 is not None
    assert seg1.id == 1

    # At 15 mins (boundary) -> 15-30
    seg2 = assign_event_to_segment(segments, 900)
    assert seg2 is not None
    assert seg2.id == 2

    # At halftime marker (1800) -> Should skip halftime and go to 30-45
    seg3 = assign_event_to_segment(segments, 1800)
    assert seg3 is not None
    assert seg3.id == 4

    # Out of bounds
    seg4 = assign_event_to_segment(segments, 5000)
    assert seg4 is None
