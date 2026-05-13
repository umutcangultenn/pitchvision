"""
Tactical analytics modülleri için unit testler.
"""
import pytest
import numpy as np
from typing import List
from app.analytics.types import (
    TrackPoint, PlayerRole, AlertType, AlertSeverity, TacticalConfig
)
from app.analytics.team_shape import (
    calculate_team_shape, calculate_block_gaps
)
from app.analytics.defensive_line import (
    calculate_defensive_line_errors, detect_defensive_line_break
)
from app.analytics.transitions import (
    calculate_transition_speed, analyze_team_transition
)
from app.analytics.runs import (
    detect_depth_run_candidate, analyze_wing_overload
)
from app.analytics.alerts_new import (
    generate_tactical_alerts, filter_alerts_by_priority, create_alert_summary
)
from app.analytics.player_scores import (
    calculate_tactical_score, calculate_physical_score
)
from app.analytics.drill_mapping import (
    get_drill_recommendations, create_training_session
)


def create_mock_track_point(
    player_id: int,
    team_id: int,
    role: PlayerRole,
    x: float,
    y: float,
    timestamp: float = 0.0,
    speed: float = None
) -> TrackPoint:
    """Mock TrackPoint oluşturur."""
    return TrackPoint(
        player_id=player_id,
        team_id=team_id,
        role=role,
        timestamp=timestamp,
        x=x,
        y=y,
        speed=speed
    )


class TestTeamShape:
    """Takım şekli analizi testleri."""
    
    def test_calculate_team_shape_basic(self):
        """Temel takım şekli hesaplama testi."""
        points = [
            create_mock_track_point(1, 1, PlayerRole.DEFENDER, 10, 20),
            create_mock_track_point(2, 1, PlayerRole.DEFENDER, 15, 25),
            create_mock_track_point(3, 1, PlayerRole.MIDFIELDER, 25, 22),
            create_mock_track_point(4, 1, PlayerRole.FORWARD, 35, 24)
        ]
        
        shape = calculate_team_shape(points)
        
        assert shape.team_length == 25.0  # 35 - 10
        assert shape.team_width == 5.0   # 25 - 20
        assert shape.centroid_x == 21.25  # (10+15+25+35)/4
        assert shape.centroid_y == 22.75  # (20+25+22+24)/4
        assert shape.compactness > 0
    
    def test_calculate_team_shape_empty_list(self):
        """Boş liste ile test."""
        with pytest.raises(ValueError):
            calculate_team_shape([])
    
    def test_calculate_block_gaps(self):
        """Blok mesafeleri hesaplama testi."""
        points = [
            create_mock_track_point(1, 1, PlayerRole.DEFENDER, 10, 20),
            create_mock_track_point(2, 1, PlayerRole.DEFENDER, 12, 25),
            create_mock_track_point(3, 1, PlayerRole.MIDFIELDER, 25, 22),
            create_mock_track_point(4, 1, PlayerRole.MIDFIELDER, 27, 24),
            create_mock_track_point(5, 1, PlayerRole.FORWARD, 40, 23)
        ]
        
        gaps = calculate_block_gaps(points)
        
        # Savunma ortalama: (10+12)/2 = 11
        # Orta saha ortalama: (25+27)/2 = 26
        # Forvet ortalama: 40
        assert gaps.defensive_midfield_gap == 15.0  # |26 - 11|
        assert gaps.midfield_forward_gap == 14.0   # |40 - 26|


class TestDefensiveLine:
    """Savunma hattı analizi testleri."""
    
    def test_calculate_defensive_line_errors(self):
        """Savunma hattı hata hesaplama testi."""
        defenders = [
            create_mock_track_point(1, 1, PlayerRole.DEFENDER, 10, 20),
            create_mock_track_point(2, 1, PlayerRole.DEFENDER, 12, 25),
            create_mock_track_point(3, 1, PlayerRole.DEFENDER, 8, 30),
            create_mock_track_point(4, 1, PlayerRole.DEFENDER, 14, 35)
        ]
        
        errors = calculate_defensive_line_errors(defenders)
        
        assert len(errors) == 4
        # Ortalama x pozisyonu: (10+12+8+14)/4 = 11
        assert errors[0].line_x == 11.0
        assert errors[0].line_error == 1.0  # |10 - 11|
        assert errors[1].line_error == 1.0  # |12 - 11|
        assert errors[2].line_error == 3.0  # |8 - 11|
        assert errors[3].line_error == 3.0  # |14 - 11|
    
    def test_detect_defensive_line_break(self):
        """Savunma hattı bozulması tespit testi."""
        # Bozuk savunma hattı
        defenders = [
            create_mock_track_point(1, 1, PlayerRole.DEFENDER, 10, 20, 100.0),
            create_mock_track_point(2, 1, PlayerRole.DEFENDER, 12, 25, 100.0),
            create_mock_track_point(3, 1, PlayerRole.DEFENDER, 20, 30, 100.0),  # Çok ileri
            create_mock_track_point(4, 1, PlayerRole.DEFENDER, 11, 35, 100.0)
        ]
        
        alert = detect_defensive_line_break(defenders, threshold_m=4.0)
        
        assert alert is not None
        assert alert.alert_type == AlertType.DEFENSIVE_LINE_BREAK
        assert alert.severity in [AlertSeverity.MEDIUM, AlertSeverity.HIGH]
        assert alert.team_id == 1
    
    def test_detect_defensive_line_break_good_line(self):
        """İyi savunma hattı testi."""
        defenders = [
            create_mock_track_point(1, 1, PlayerRole.DEFENDER, 10, 20, 100.0),
            create_mock_track_point(2, 1, PlayerRole.DEFENDER, 11, 25, 100.0),
            create_mock_track_point(3, 1, PlayerRole.DEFENDER, 9, 30, 100.0),
            create_mock_track_point(4, 1, PlayerRole.DEFENDER, 10, 35, 100.0)
        ]
        
        alert = detect_defensive_line_break(defenders, threshold_m=4.0)
        
        assert alert is None  # İyi hat, uyarı yok


class TestTransitions:
    """Geçiş oyunu analizi testleri."""
    
    def test_calculate_transition_speed(self):
        """Geçiş hızı hesaplama testi."""
        speed = calculate_transition_speed(10.0, 30.0, 5.0)
        assert speed == 4.0  # (30-10)/5
        
        # Sıfır zaman testi
        speed = calculate_transition_speed(10.0, 30.0, 0.0)
        assert speed == 0.0
    
    def test_analyze_team_transition(self):
        """Takım geçiş analizi testi."""
        start_positions = [
            create_mock_track_point(1, 1, PlayerRole.DEFENDER, 20, 20, 100.0),
            create_mock_track_point(2, 1, PlayerRole.MIDFIELDER, 25, 25, 100.0),
            create_mock_track_point(3, 1, PlayerRole.FORWARD, 30, 30, 100.0)
        ]
        
        end_positions = [
            create_mock_track_point(1, 1, PlayerRole.DEFENDER, 25, 20, 105.0),
            create_mock_track_point(2, 1, PlayerRole.MIDFIELDER, 35, 25, 105.0),
            create_mock_track_point(3, 1, PlayerRole.FORWARD, 45, 30, 105.0)
        ]
        
        metrics = analyze_team_transition(start_positions, end_positions, "attack")
        
        assert metrics.start_x == 25.0  # (20+25+30)/3
        assert metrics.end_x == 35.0   # (25+35+45)/3
        assert metrics.duration == 5.0
        assert metrics.speed == 2.0    # (35-25)/5
        assert metrics.player_count == 3


class TestRuns:
    """Koşu analizi testleri."""
    
    def test_analyze_wing_overload(self):
        """Kanat yüklenmesi analizi testi."""
        # Sağ kanatta yükleme
        players = [
            create_mock_track_point(1, 1, PlayerRole.MIDFIELDER, 30, 50),  # Sağ kanat
            create_mock_track_point(2, 1, PlayerRole.FORWARD, 35, 55),    # Sağ kanat
            create_mock_track_point(3, 1, PlayerRole.FORWARD, 40, 60),    # Sağ kanat
            create_mock_track_point(4, 1, PlayerRole.MIDFIELDER, 25, 30), # Merkez
        ]
        
        analysis = analyze_wing_overload(players, "right", field_width=68.0)
        
        assert analysis["overload_detected"] == True
        assert analysis["player_count"] == 3
        assert analysis["wing_side"] == "right"
        assert analysis["overload_intensity"] > 0.4


class TestPlayerScores:
    """Oyuncu skor testleri."""
    
    def test_calculate_physical_score(self):
        """Fiziksel skor hesaplama testi."""
        positions = [
            create_mock_track_point(1, 1, PlayerRole.MIDFIELDER, 20, 20, 0.0),
            create_mock_track_point(1, 1, PlayerRole.MIDFIELDER, 25, 22, 1.0),
            create_mock_track_point(1, 1, PlayerRole.MIDFIELDER, 30, 25, 2.0),
            create_mock_track_point(1, 1, PlayerRole.MIDFIELDER, 35, 28, 3.0)
        ]
        
        score = calculate_physical_score(positions)
        
        assert 0 <= score <= 10
        assert isinstance(score, float)
    
    def test_calculate_tactical_score(self):
        """Taktiksel skor hesaplama testi."""
        player_positions = [
            create_mock_track_point(1, 1, PlayerRole.MIDFIELDER, 25, 25, 0.0),
            create_mock_track_point(1, 1, PlayerRole.MIDFIELDER, 26, 26, 1.0)
        ]
        
        team_positions = [
            create_mock_track_point(2, 1, PlayerRole.DEFENDER, 20, 20, 1.0),
            create_mock_track_point(3, 1, PlayerRole.FORWARD, 30, 30, 1.0)
        ]
        
        opponent_positions = [
            create_mock_track_point(4, 2, PlayerRole.MIDFIELDER, 35, 25, 1.0)
        ]
        
        score = calculate_tactical_score(player_positions, team_positions, opponent_positions)
        
        assert 0 <= score <= 10
        assert isinstance(score, float)


class TestTacticalAlerts:
    """Taktiksel uyarı testleri."""
    
    def test_generate_tactical_alerts(self):
        """Taktiksel uyarı üretme testi."""
        tracking_data = [
            # Takım 1 - bozuk savunma hattı
            create_mock_track_point(1, 1, PlayerRole.DEFENDER, 10, 20, 100.0),
            create_mock_track_point(2, 1, PlayerRole.DEFENDER, 12, 25, 100.0),
            create_mock_track_point(3, 1, PlayerRole.DEFENDER, 20, 30, 100.0),  # Çok ileri
            create_mock_track_point(4, 1, PlayerRole.MIDFIELDER, 30, 25, 100.0),
            create_mock_track_point(5, 1, PlayerRole.FORWARD, 40, 28, 100.0),
        ]
        
        alerts = generate_tactical_alerts(tracking_data, team_id=1, timestamp=100.0)
        
        assert len(alerts) >= 0  # En az bir uyarı olmalı
        
        # Savunma hattı uyarısı kontrol et
        defensive_alerts = [a for a in alerts if a.alert_type == AlertType.DEFENSIVE_LINE_BREAK]
        assert len(defensive_alerts) > 0


# Mock veri oluşturma yardımcı fonksiyonları
def create_mock_match_data(team_count: int = 2, players_per_team: int = 11) -> List[TrackPoint]:
    """Mock maç verisi oluşturur."""
    data = []
    
    for team_id in range(1, team_count + 1):
        for player_id in range(1, players_per_team + 1):
            # Pozisyon rolü belirle
            if player_id == 1:
                role = PlayerRole.GOALKEEPER
            elif player_id <= 5:
                role = PlayerRole.DEFENDER
            elif player_id <= 9:
                role = PlayerRole.MIDFIELDER
            else:
                role = PlayerRole.FORWARD
            
            # Rastgele pozisyon
            x = np.random.uniform(5, 100)
            y = np.random.uniform(5, 63)
            speed = np.random.uniform(0, 8)
            
            point = create_mock_track_point(
                player_id=player_id + (team_id - 1) * players_per_team,
                team_id=team_id,
                role=role,
                x=x,
                y=y,
                timestamp=100.0,
                speed=speed
            )
            data.append(point)
    
    return data


if __name__ == "__main__":
    # Testleri çalıştır
    pytest.main([__file__, "-v"])