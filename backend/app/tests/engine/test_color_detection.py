import pytest
import numpy as np
from app.engine.color_detection import _name_color_hsv, infer_attacking_direction, CV2_AVAILABLE, SKLEARN_AVAILABLE


def test_name_color_hsv():
    """Test HSV to human-readable color naming."""
    assert _name_color_hsv(0, 255, 255) == "red"
    assert _name_color_hsv(110, 255, 255) == "blue"
    assert _name_color_hsv(60, 255, 255) == "green"
    assert _name_color_hsv(30, 255, 255) == "yellow"
    assert _name_color_hsv(150, 255, 255) == "purple"

    # Low brightness
    assert _name_color_hsv(100, 100, 30) == "black"
    
    # Low saturation, high brightness
    assert _name_color_hsv(100, 10, 200) == "white"


def test_infer_attacking_direction():
    """Test inference of attacking direction from team centroid."""
    field_length = 100.0

    # Team in defensive half (left) -> Attacking right
    pos_left = [(10, 30), (20, 20), (30, 40), (15, 50)]
    assert infer_attacking_direction(pos_left, field_length) == "left_to_right"

    # Team in attacking half (right) -> Attacking left
    pos_right = [(80, 30), (90, 20), (70, 40), (85, 50)]
    assert infer_attacking_direction(pos_right, field_length) == "right_to_left"

    # Centered / uncertain
    pos_center = [(45, 30), (55, 20), (50, 40)]
    assert infer_attacking_direction(pos_center, field_length) == "uncertain"

    # Not enough players
    assert infer_attacking_direction([(10, 10)], field_length) == "uncertain"
