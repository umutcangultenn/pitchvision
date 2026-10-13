"""
PitchCalibrator unit testleri — compute_homography ve pixel_to_field dönüşümleri.
"""
import pytest
import numpy as np
from app.cv.calibration import PitchCalibrator


@pytest.fixture
def calibrator() -> PitchCalibrator:
    return PitchCalibrator()


@pytest.fixture
def calibrator_with_points(calibrator: PitchCalibrator) -> PitchCalibrator:
    """4 köşe noktasıyla kalibre edilmiş kalibratör."""
    calibrator.set_calibration_points([
        {"pixel": [0,    0   ], "real": [0.0,   0.0 ]},
        {"pixel": [1920, 0   ], "real": [105.0, 0.0 ]},
        {"pixel": [1920, 1080], "real": [105.0, 68.0]},
        {"pixel": [0,    1080], "real": [0.0,   68.0]},
    ])
    return calibrator


class TestPitchCalibratorInit:
    def test_default_dimensions(self, calibrator):
        assert calibrator.pitch_length == 105.0
        assert calibrator.pitch_width  == 68.0

    def test_no_homography_initially(self, calibrator):
        assert calibrator.homography_matrix is None

    def test_calibration_points_empty(self, calibrator):
        assert calibrator.calibration_points == []


class TestSetCalibrationPoints:
    def test_fewer_than_four_no_homography(self, calibrator):
        calibrator.set_calibration_points([
            {"pixel": [0, 0], "real": [0.0, 0.0]},
            {"pixel": [100, 0], "real": [10.0, 0.0]},
        ])
        assert calibrator.homography_matrix is None

    def test_four_points_sets_homography(self, calibrator_with_points):
        assert calibrator_with_points.homography_matrix is not None

    def test_homography_is_3x3(self, calibrator_with_points):
        H = calibrator_with_points.homography_matrix
        assert H.shape == (3, 3)


class TestPixelToReal:
    def test_returns_tuple(self, calibrator):
        result = calibrator.pixel_to_real((100.0, 200.0))
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_origin_pixel(self, calibrator):
        """(0,0) pikseli → (0,0) gerçek koordinat."""
        rx, ry = calibrator.pixel_to_real((0.0, 0.0))
        assert rx == pytest.approx(0.0)
        assert ry == pytest.approx(0.0)

    def test_scale_factor(self, calibrator):
        """Varsayılan 0.05 ölçek faktörü."""
        rx, ry = calibrator.pixel_to_real((100.0, 200.0))
        assert rx == pytest.approx(5.0)
        assert ry == pytest.approx(10.0)


class TestRealToPixel:
    def test_returns_tuple(self, calibrator):
        result = calibrator.real_to_pixel((10.0, 20.0))
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_inverse_scale(self, calibrator):
        """Varsayılan 20x ölçek faktörü."""
        px, py = calibrator.real_to_pixel((5.0, 10.0))
        assert px == pytest.approx(100.0)
        assert py == pytest.approx(200.0)


class TestCalculateDistance:
    def test_zero_distance(self, calibrator):
        assert calibrator.calculate_distance((100, 100), (100, 100)) == pytest.approx(0.0)

    def test_known_distance(self, calibrator):
        """(0,0) → (100,0) pikseli = 5m mesafe (0.05 ölçek)."""
        dist = calibrator.calculate_distance((0, 0), (100, 0))
        assert dist == pytest.approx(5.0)

    def test_diagonal_distance(self, calibrator):
        """Pisagor teoremi ile doğrulama."""
        # pixel (0,0) → (60,80) = real (3,4) → mesafe = 5
        dist = calibrator.calculate_distance((0, 0), (60, 80))
        assert dist == pytest.approx(5.0)


class TestGetPitchZones:
    def test_returns_all_zones(self, calibrator):
        zones = calibrator.get_pitch_zones()
        expected = {
            "defensive_third", "middle_third", "attacking_third",
            "left_wing", "center", "right_wing",
        }
        assert set(zones.keys()) == expected

    def test_zone_x_ranges_cover_full_pitch(self, calibrator):
        zones = calibrator.get_pitch_zones()
        assert zones["defensive_third"]["x"][0] == 0
        assert zones["attacking_third"]["x"][1] == 105

    def test_zone_y_ranges_cover_full_width(self, calibrator):
        zones = calibrator.get_pitch_zones()
        assert zones["left_wing"]["y"][0] == 0
        assert zones["right_wing"]["y"][1] == pytest.approx(68.0, abs=0.1)
