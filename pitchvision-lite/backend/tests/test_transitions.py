"""
calculate_transition_speed ve analyze_team_transition unit testleri.
"""
import pytest
from app.analytics.types import AlertType, AlertSeverity, TacticalConfig, PlayerRole
from app.analytics.transitions import (
    calculate_transition_speed,
    analyze_team_transition,
    detect_slow_transition_alert,
    detect_slow_transition_alert_detailed,
)
from tests.conftest import make_point


class TestCalculateTransitionSpeed:
    def test_basic(self):
        assert calculate_transition_speed(10.0, 30.0, 5.0) == pytest.approx(4.0)

    def test_zero_seconds_returns_zero(self):
        assert calculate_transition_speed(10.0, 30.0, 0.0) == 0.0

    def test_negative_seconds_returns_zero(self):
        assert calculate_transition_speed(10.0, 30.0, -1.0) == 0.0

    def test_backward_movement(self):
        """Geri hareket de mesafe olarak hesaplanmalı."""
        assert calculate_transition_speed(30.0, 10.0, 5.0) == pytest.approx(4.0)

    def test_no_movement(self):
        assert calculate_transition_speed(20.0, 20.0, 5.0) == 0.0


class TestAnalyzeTeamTransition:
    def _make_team(self, x_offset: float, timestamp: float):
        return [
            make_point(1, 1, PlayerRole.DEFENDER,   20.0 + x_offset, 20.0, timestamp),
            make_point(2, 1, PlayerRole.MIDFIELDER, 30.0 + x_offset, 34.0, timestamp),
            make_point(3, 1, PlayerRole.FORWARD,    40.0 + x_offset, 48.0, timestamp),
        ]

    def test_attack_transition(self):
        start = self._make_team(0.0, 100.0)
        end   = self._make_team(10.0, 105.0)

        metrics = analyze_team_transition(start, end, "attack")

        assert metrics.start_x == pytest.approx(30.0)
        assert metrics.end_x   == pytest.approx(40.0)
        assert metrics.duration == pytest.approx(5.0)
        assert metrics.speed    == pytest.approx(2.0)
        assert metrics.player_count == 3

    def test_empty_positions_returns_zero_metrics(self):
        metrics = analyze_team_transition([], [], "attack")
        assert metrics.speed == 0.0
        assert metrics.player_count == 0

    def test_successful_attack_transition(self):
        """İleri hareket + yeterli hız → başarılı geçiş."""
        start = self._make_team(0.0,  100.0)
        end   = self._make_team(20.0, 103.0)  # 20m / 3s ≈ 6.67 m/s

        metrics = analyze_team_transition(start, end, "attack")
        assert metrics.success is True

    def test_slow_attack_transition_not_successful(self):
        """Çok yavaş ileri hareket → başarısız."""
        start = self._make_team(0.0, 100.0)
        end   = self._make_team(1.0, 110.0)   # 1m / 10s = 0.1 m/s

        metrics = analyze_team_transition(start, end, "attack")
        assert metrics.success is False


class TestDetectSlowTransitionAlert:
    def test_fast_players_no_alert(self):
        players = [
            make_point(i, 1, PlayerRole.MIDFIELDER, 30.0, float(i * 10), 100.0, speed=5.0)
            for i in range(1, 8)
        ]
        alert = detect_slow_transition_alert(players, (35.0, 34.0), 100.0)
        assert alert is None

    def test_slow_players_produce_alert(self):
        players = [
            make_point(i, 1, PlayerRole.MIDFIELDER, 30.0, float(i * 10), 100.0, speed=1.0)
            for i in range(1, 8)
        ]
        alert = detect_slow_transition_alert(players, (35.0, 34.0), 100.0)
        assert alert is not None
        assert alert.alert_type == AlertType.TRANSITION_SLOW
        assert 0.0 < alert.confidence <= 1.0

    def test_too_few_players_returns_none(self):
        players = [
            make_point(i, 1, PlayerRole.MIDFIELDER, 30.0, float(i * 10), 100.0, speed=1.0)
            for i in range(1, 4)
        ]
        assert detect_slow_transition_alert(players, (35.0, 34.0), 100.0) is None


class TestDetectSlowTransitionAlertDetailed:
    def _make_metrics(self, speed: float):
        from app.analytics.types import TransitionMetrics
        return TransitionMetrics(
            start_x=20.0, end_x=20.0 + speed * 5,
            duration=5.0, speed=speed,
            player_count=5, success=speed >= TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD,
        )

    def test_fast_transition_no_alert(self):
        metrics = self._make_metrics(5.0)
        assert detect_slow_transition_alert_detailed(metrics, 1, 100.0) is None

    def test_slow_transition_alert(self):
        metrics = self._make_metrics(1.5)
        alert = detect_slow_transition_alert_detailed(metrics, 1, 100.0)
        assert alert is not None
        assert alert.severity == AlertSeverity.MEDIUM

    def test_very_slow_transition_high_severity(self):
        metrics = self._make_metrics(0.5)
        alert = detect_slow_transition_alert_detailed(metrics, 1, 100.0)
        assert alert is not None
        assert alert.severity == AlertSeverity.HIGH
