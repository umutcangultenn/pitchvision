"""
generate_tactical_alerts, filter_alerts_by_priority, create_alert_summary
ve drill_mapping unit testleri.
"""
import pytest
from app.analytics.types import (
    AlertType, AlertSeverity, TacticalAlert, PlayerRole, TacticalConfig,
)
from app.analytics.alerts_new import (
    generate_tactical_alerts,
    filter_alerts_by_priority,
    create_alert_summary,
    detect_block_gap_alert,
    detect_compactness_alert,
)
from app.analytics.drill_mapping import (
    get_drill_recommendations,
    create_training_session,
    get_drill_by_focus_area,
    get_equipment_list,
    DRILL_DATABASE,
)
from tests.conftest import make_point


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_alert(
    atype: AlertType,
    severity: AlertSeverity,
    confidence: float,
    timestamp: float = 100.0,
    team_id: int = 1,
) -> TacticalAlert:
    return TacticalAlert(
        alert_type=atype,
        timestamp=timestamp,
        confidence=confidence,
        severity=severity,
        description="test",
        metadata={},
        team_id=team_id,
    )


# ── generate_tactical_alerts ──────────────────────────────────────────────────

class TestGenerateTacticalAlerts:
    def test_broken_line_produces_defensive_alert(self, broken_defenders):
        """Bozuk savunma hattı → DEFENSIVE_LINE_BREAK uyarısı."""
        alerts = generate_tactical_alerts(broken_defenders, team_id=1, timestamp=100.0)
        types = [a.alert_type for a in alerts]
        assert AlertType.DEFENSIVE_LINE_BREAK in types

    def test_empty_data_returns_empty(self):
        alerts = generate_tactical_alerts([], team_id=1, timestamp=0.0)
        assert alerts == []

    def test_wrong_team_id_returns_empty(self, standard_team):
        alerts = generate_tactical_alerts(standard_team, team_id=99, timestamp=100.0)
        assert alerts == []

    def test_spread_team_produces_compactness_alert(self, spread_team):
        alerts = generate_tactical_alerts(spread_team, team_id=1, timestamp=100.0)
        types = [a.alert_type for a in alerts]
        assert AlertType.COMPACTNESS_LOST in types

    def test_all_alerts_have_valid_confidence(self, standard_team):
        alerts = generate_tactical_alerts(standard_team, team_id=1, timestamp=100.0)
        for a in alerts:
            assert 0.0 <= a.confidence <= 1.0

    def test_all_alerts_have_team_id(self, standard_team):
        alerts = generate_tactical_alerts(standard_team, team_id=1, timestamp=100.0)
        for a in alerts:
            assert a.team_id == 1


class TestDetectBlockGapAlert:
    def test_below_threshold_no_alert(self):
        assert detect_block_gap_alert(10.0, 10.0, 1, 100.0) is None

    def test_warning_threshold(self):
        alert = detect_block_gap_alert(
            TacticalConfig.BLOCK_GAP_WARNING_THRESHOLD + 1,
            10.0, 1, 100.0,
        )
        assert alert is not None
        assert alert.alert_type == AlertType.BLOCK_GAP_WIDE
        assert alert.severity == AlertSeverity.MEDIUM

    def test_critical_threshold(self):
        alert = detect_block_gap_alert(
            TacticalConfig.BLOCK_GAP_CRITICAL_THRESHOLD + 1,
            10.0, 1, 100.0,
        )
        assert alert is not None
        assert alert.severity == AlertSeverity.HIGH


class TestDetectCompactnessAlert:
    def test_compact_team_no_alert(self):
        assert detect_compactness_alert(10.0, 1, 100.0) is None

    def test_warning_compactness(self):
        alert = detect_compactness_alert(
            TacticalConfig.COMPACTNESS_WARNING_THRESHOLD + 1, 1, 100.0
        )
        assert alert is not None
        assert alert.alert_type == AlertType.COMPACTNESS_LOST

    def test_critical_compactness(self):
        alert = detect_compactness_alert(
            TacticalConfig.COMPACTNESS_CRITICAL_THRESHOLD + 1, 1, 100.0
        )
        assert alert is not None
        assert alert.severity == AlertSeverity.HIGH


# ── filter_alerts_by_priority ─────────────────────────────────────────────────

class TestFilterAlertsByPriority:
    def test_empty_returns_empty(self):
        assert filter_alerts_by_priority([]) == []

    def test_respects_max_alerts(self):
        alerts = [
            _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.LOW, 0.5)
            for _ in range(10)
        ]
        result = filter_alerts_by_priority(alerts, max_alerts=3)
        assert len(result) == 3

    def test_high_severity_first(self):
        alerts = [
            _make_alert(AlertType.COMPACTNESS_LOST,       AlertSeverity.LOW,      0.9),
            _make_alert(AlertType.DEFENSIVE_LINE_BREAK,   AlertSeverity.CRITICAL, 0.9),
            _make_alert(AlertType.BLOCK_GAP_WIDE,         AlertSeverity.MEDIUM,   0.9),
        ]
        result = filter_alerts_by_priority(alerts, max_alerts=3)
        assert result[0].severity == AlertSeverity.CRITICAL

    def test_same_severity_higher_confidence_first(self):
        alerts = [
            _make_alert(AlertType.COMPACTNESS_LOST,     AlertSeverity.HIGH, 0.4),
            _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.HIGH, 0.9),
        ]
        result = filter_alerts_by_priority(alerts)
        assert result[0].confidence == pytest.approx(0.9)


# ── create_alert_summary ──────────────────────────────────────────────────────

class TestCreateAlertSummary:
    def test_empty_alerts(self):
        summary = create_alert_summary([])
        assert summary["total_alerts"] == 0
        assert summary["most_frequent"] is None
        assert summary["highest_priority"] is None

    def test_counts_correctly(self):
        alerts = [
            _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.HIGH,   0.8),
            _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.MEDIUM, 0.6),
            _make_alert(AlertType.COMPACTNESS_LOST,     AlertSeverity.LOW,    0.4),
        ]
        summary = create_alert_summary(alerts)
        assert summary["total_alerts"] == 3
        assert summary["by_type"]["defensive_line_break"] == 2
        assert summary["most_frequent"]["type"] == "defensive_line_break"

    def test_highest_priority_is_critical(self):
        alerts = [
            _make_alert(AlertType.BLOCK_GAP_WIDE,       AlertSeverity.LOW,      0.9),
            _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.CRITICAL, 0.5),
        ]
        summary = create_alert_summary(alerts)
        assert summary["highest_priority"]["severity"] == "critical"


# ── drill_mapping ─────────────────────────────────────────────────────────────

class TestGetDrillRecommendations:
    def test_known_alert_type_returns_drills(self):
        alert = _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.HIGH, 0.8)
        drills = get_drill_recommendations(alert, team_level="youth", available_time=30, player_count=11)
        assert len(drills) > 0

    def test_unknown_alert_type_returns_empty(self):
        alert = _make_alert(AlertType.OFFSIDE_TRAP_FAILED, AlertSeverity.LOW, 0.5)
        drills = get_drill_recommendations(alert)
        assert drills == []

    def test_time_filter(self):
        alert = _make_alert(AlertType.BLOCK_GAP_WIDE, AlertSeverity.MEDIUM, 0.7)
        drills = get_drill_recommendations(alert, available_time=5)
        for d in drills:
            assert d.duration_minutes <= 5

    def test_youth_no_hard_drills(self):
        alert = _make_alert(AlertType.TRANSITION_SLOW, AlertSeverity.HIGH, 0.8)
        drills = get_drill_recommendations(alert, team_level="youth", available_time=60)
        for d in drills:
            assert d.difficulty != "hard"

    def test_max_three_recommendations(self):
        alert = _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.HIGH, 0.9)
        drills = get_drill_recommendations(alert, available_time=60, player_count=11)
        assert len(drills) <= 3


class TestCreateTrainingSession:
    def test_basic_session_structure(self):
        alerts = [
            _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.HIGH,   0.8),
            _make_alert(AlertType.BLOCK_GAP_WIDE,       AlertSeverity.MEDIUM, 0.6),
        ]
        session = create_training_session(alerts, session_duration=90)

        assert "warm_up"     in session
        assert "main_drills" in session
        assert "cool_down"   in session
        assert session["total_duration"] == 90

    def test_empty_alerts_still_valid(self):
        session = create_training_session([], session_duration=60)
        assert session["total_duration"] == 60

    def test_high_priority_alerts_processed_first(self):
        alerts = [
            _make_alert(AlertType.COMPACTNESS_LOST,     AlertSeverity.LOW,      0.5),
            _make_alert(AlertType.DEFENSIVE_LINE_BREAK, AlertSeverity.CRITICAL, 0.9),
        ]
        session = create_training_session(alerts, session_duration=90, team_level="professional")
        if session["main_drills"]:
            first_drill = session["main_drills"][0]
            assert first_drill["alert_type"] == AlertType.DEFENSIVE_LINE_BREAK.value


class TestGetDrillByFocusArea:
    def test_known_focus_area(self):
        drills = get_drill_by_focus_area("defensive_line")
        assert len(drills) > 0

    def test_unknown_focus_area_returns_empty(self):
        drills = get_drill_by_focus_area("nonexistent_area")
        assert drills == []


class TestGetEquipmentList:
    def test_deduplicates_equipment(self):
        drills = list(DRILL_DATABASE[AlertType.DEFENSIVE_LINE_BREAK])
        equipment = get_equipment_list(drills)
        assert len(equipment) == len(set(equipment))

    def test_empty_drills_returns_empty(self):
        assert get_equipment_list([]) == []
