"""
calculate_team_shape ve calculate_block_gaps unit testleri.
"""
import pytest
from app.analytics.types import PlayerRole, TacticalConfig
from app.analytics.team_shape import (
    calculate_team_shape,
    calculate_block_gaps,
    calculate_team_width_by_thirds,
    calculate_formation_compactness,
)
from tests.conftest import make_point


class TestCalculateTeamShape:
    def test_basic_geometry(self):
        points = [
            make_point(1, 1, PlayerRole.DEFENDER,   10.0, 20.0),
            make_point(2, 1, PlayerRole.MIDFIELDER, 25.0, 25.0),
            make_point(3, 1, PlayerRole.FORWARD,    35.0, 22.0),
        ]
        shape = calculate_team_shape(points)

        assert shape.team_length == pytest.approx(25.0)   # 35 - 10
        assert shape.team_width  == pytest.approx(5.0)    # 25 - 20
        assert shape.centroid_x  == pytest.approx(23.33, abs=0.1)
        assert shape.compactness > 0

    def test_single_player(self):
        points = [make_point(1, 1, PlayerRole.MIDFIELDER, 30.0, 34.0)]
        shape = calculate_team_shape(points)

        assert shape.team_length == 0.0
        assert shape.team_width  == 0.0
        assert shape.compactness == 0.0

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            calculate_team_shape([])

    def test_standard_team(self, standard_team):
        shape = calculate_team_shape(standard_team)

        assert shape.team_length > 0
        assert shape.team_width  > 0
        assert 0 < shape.centroid_x < TacticalConfig.FIELD_LENGTH
        assert 0 < shape.centroid_y < TacticalConfig.FIELD_WIDTH

    def test_spread_team_higher_compactness(self, standard_team, spread_team):
        """Dağınık takımın kompaktlık değeri daha yüksek olmalı."""
        compact_shape = calculate_team_shape(standard_team)
        spread_shape  = calculate_team_shape(spread_team)
        assert spread_shape.compactness > compact_shape.compactness


class TestCalculateBlockGaps:
    def test_known_gaps(self):
        points = [
            make_point(1, 1, PlayerRole.DEFENDER,   10.0, 20.0),
            make_point(2, 1, PlayerRole.DEFENDER,   12.0, 40.0),
            make_point(3, 1, PlayerRole.MIDFIELDER, 25.0, 22.0),
            make_point(4, 1, PlayerRole.MIDFIELDER, 27.0, 44.0),
            make_point(5, 1, PlayerRole.FORWARD,    40.0, 34.0),
        ]
        gaps = calculate_block_gaps(points)

        # def avg = 11, mid avg = 26, fwd avg = 40
        assert gaps.defensive_midfield_gap == pytest.approx(15.0)
        assert gaps.midfield_forward_gap   == pytest.approx(14.0)

    def test_missing_block_returns_zero(self):
        """Forvet yoksa midfield_forward_gap sıfır olmalı."""
        points = [
            make_point(1, 1, PlayerRole.DEFENDER,   10.0, 20.0),
            make_point(2, 1, PlayerRole.MIDFIELDER, 25.0, 34.0),
        ]
        gaps = calculate_block_gaps(points)
        assert gaps.midfield_forward_gap == 0.0

    def test_all_same_role(self):
        """Tek rol varsa diğer gap sıfır olmalı."""
        points = [make_point(i, 1, PlayerRole.MIDFIELDER, float(i * 5), 34.0) for i in range(1, 5)]
        gaps = calculate_block_gaps(points)
        assert gaps.defensive_midfield_gap == 0.0
        assert gaps.midfield_forward_gap   == 0.0


class TestTeamWidthByThirds:
    def test_returns_three_keys(self, standard_team):
        result = calculate_team_width_by_thirds(standard_team)
        assert set(result.keys()) == {"defensive_third", "middle_third", "attacking_third"}

    def test_empty_returns_zeros(self):
        result = calculate_team_width_by_thirds([])
        assert all(v == 0.0 for v in result.values())


class TestFormationCompactness:
    def test_returns_all_groups(self, standard_team):
        result = calculate_formation_compactness(standard_team)
        assert "defenders"   in result
        assert "midfielders" in result
        assert "forwards"    in result

    def test_single_player_group_zero(self):
        points = [make_point(1, 1, PlayerRole.DEFENDER, 10.0, 34.0)]
        result = calculate_formation_compactness(points)
        assert result["defenders"] == 0.0
