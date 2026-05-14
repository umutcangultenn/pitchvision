"""
calculate_defensive_line_errors ve detect_defensive_line_break unit testleri.
"""
import pytest
from app.analytics.types import AlertType, AlertSeverity, TacticalConfig
from app.analytics.defensive_line import (
    calculate_defensive_line_errors,
    detect_defensive_line_break,
    analyze_offside_trap_effectiveness,
    calculate_defensive_line_height,
)
from tests.conftest import make_point
from app.analytics.types import PlayerRole


class TestCalculateDefensiveLineErrors:
    def test_known_errors(self):
        defenders = [
            make_point(1, 1, PlayerRole.DEFENDER, 10.0, 15.0),
            make_point(2, 1, PlayerRole.DEFENDER, 12.0, 25.0),
            make_point(3, 1, PlayerRole.DEFENDER,  8.0, 40.0),
            make_point(4, 1, PlayerRole.DEFENDER, 14.0, 55.0),
        ]
        errors = calculate_defensive_line_errors(defenders)

        # avg_x = (10+12+8+14)/4 = 11
        assert len(errors) == 4
        assert errors[0].line_x == pytest.approx(11.0)
        assert errors[0].line_error == pytest.approx(1.0)   # |10-11|
        assert errors[2].line_error == pytest.approx(3.0)   # |8-11|

    def test_single_defender_returns_empty(self):
        defenders = [make_point(1, 1, PlayerRole.DEFENDER, 10.0, 34.0)]
        assert calculate_defensive_line_errors(defenders) == []

    def test_offside_trap_flag(self):
        """Hat önündeki oyuncu ofsayt tuzağı riski taşımalı."""
        defenders = [
            make_point(1, 1, PlayerRole.DEFENDER, 10.0, 20.0),
            make_point(2, 1, PlayerRole.DEFENDER, 15.0, 40.0),  # ileri
        ]
        errors = calculate_defensive_line_errors(defenders)
        # avg = 12.5; player2.x=15 > 12.5 → is_offside_trap=True
        assert errors[1].is_offside_trap is True
        assert errors[0].is_offside_trap is False


class TestDetectDefensiveLineBreak:
    def test_broken_line_produces_alert(self, broken_defenders):
        alert = detect_defensive_line_break(broken_defenders, threshold_m=4.0)

        assert alert is not None
        assert alert.alert_type == AlertType.DEFENSIVE_LINE_BREAK
        assert alert.severity in (AlertSeverity.MEDIUM, AlertSeverity.HIGH)
        assert 0.0 < alert.confidence <= 1.0
        assert alert.team_id == 1

    def test_flat_line_no_alert(self, flat_defenders):
        alert = detect_defensive_line_break(flat_defenders, threshold_m=4.0)
        assert alert is None

    def test_too_few_defenders_returns_none(self):
        defenders = [
            make_point(1, 1, PlayerRole.DEFENDER, 10.0, 20.0),
            make_point(2, 1, PlayerRole.DEFENDER, 10.0, 40.0),
        ]
        assert detect_defensive_line_break(defenders) is None

    def test_high_severity_for_large_error(self):
        defenders = [
            make_point(1, 1, PlayerRole.DEFENDER, 10.0, 15.0, 100.0),
            make_point(2, 1, PlayerRole.DEFENDER, 10.0, 30.0, 100.0),
            make_point(3, 1, PlayerRole.DEFENDER, 10.0, 45.0, 100.0),
            make_point(4, 1, PlayerRole.DEFENDER, 30.0, 60.0, 100.0),  # 20 m ileri
        ]
        alert = detect_defensive_line_break(defenders, threshold_m=4.0)
        assert alert is not None
        assert alert.severity == AlertSeverity.HIGH

    def test_custom_threshold(self, flat_defenders):
        """Çok düşük eşik ile düzgün hat bile uyarı üretmeli."""
        alert = detect_defensive_line_break(flat_defenders, threshold_m=0.0)
        # flat_defenders'da tüm x=10, avg=10, error=0 → threshold=0 ile None
        assert alert is None


class TestOffsideTrapEffectiveness:
    def test_all_attackers_onside(self):
        defenders = [
            make_point(1, 1, PlayerRole.DEFENDER, 30.0, 20.0),
            make_point(2, 1, PlayerRole.DEFENDER, 30.0, 48.0),
        ]
        attackers = [
            make_point(10, 2, PlayerRole.FORWARD, 20.0, 34.0),
        ]
        result = analyze_offside_trap_effectiveness(defenders, attackers)
        assert result["offside_players"] == 0
        assert result["onside_players"] == 1

    def test_attacker_offside(self):
        defenders = [
            make_point(1, 1, PlayerRole.DEFENDER, 30.0, 20.0),
            make_point(2, 1, PlayerRole.DEFENDER, 30.0, 48.0),
        ]
        attackers = [
            make_point(10, 2, PlayerRole.FORWARD, 40.0, 34.0),  # x > 30
        ]
        result = analyze_offside_trap_effectiveness(defenders, attackers)
        assert result["offside_players"] == 1
        assert result["effectiveness"] == pytest.approx(1.0)


class TestDefensiveLineHeight:
    def test_high_line(self):
        defenders = [
            make_point(i, 1, PlayerRole.DEFENDER, 70.0, float(i * 15), 100.0)
            for i in range(1, 5)
        ]
        result = calculate_defensive_line_height(defenders)
        assert result["is_high_line"] is True
        assert result["is_deep_line"] is False

    def test_deep_line(self):
        defenders = [
            make_point(i, 1, PlayerRole.DEFENDER, 15.0, float(i * 15), 100.0)
            for i in range(1, 5)
        ]
        result = calculate_defensive_line_height(defenders)
        assert result["is_deep_line"] is True
        assert result["is_high_line"] is False

    def test_empty_returns_zeros(self):
        result = calculate_defensive_line_height([])
        assert result["average_height"] == 0.0
