"""
Analytics modülü - Taktiksel analiz ve metrik hesaplama.
"""

from .types import (
    TrackPoint, PlayerRole, AlertType, AlertSeverity, TacticalAlert,
    TeamShape, BlockGaps, DefensiveLineError, TransitionMetrics,
    DepthRunCandidate, TacticalConfig
)

from .team_shape import (
    calculate_team_shape,
    calculate_block_gaps,
    calculate_team_width_by_thirds,
    calculate_formation_compactness,
    detect_formation_pattern
)

from .defensive_line import (
    calculate_defensive_line_errors,
    detect_defensive_line_break,
    analyze_offside_trap_effectiveness,
    calculate_defensive_line_height
)

from .transitions import (
    calculate_transition_speed,
    analyze_team_transition,
    detect_slow_transition_alert,
    analyze_counter_attack_opportunity,
    calculate_pressing_intensity
)

from .runs import (
    detect_depth_run_candidate,
    analyze_space_creation_movement,
    detect_overlapping_run,
    analyze_wing_overload
)

from .alerts_new import (
    generate_tactical_alerts,
    filter_alerts_by_priority,
    create_alert_summary
)

from .player_scores import (
    calculate_tactical_score,
    calculate_physical_score,
    calculate_decision_score
)

from .drill_mapping import (
    DrillRecommendation,
    get_drill_recommendations,
    create_training_session,
    get_drill_by_focus_area
)

__all__ = [
    # Types
    'TrackPoint', 'PlayerRole', 'AlertType', 'AlertSeverity', 'TacticalAlert',
    'TeamShape', 'BlockGaps', 'DefensiveLineError', 'TransitionMetrics',
    'DepthRunCandidate', 'TacticalConfig',
    
    # Team Shape
    'calculate_team_shape', 'calculate_block_gaps', 'calculate_team_width_by_thirds',
    'calculate_formation_compactness', 'detect_formation_pattern',
    
    # Defensive Line
    'calculate_defensive_line_errors', 'detect_defensive_line_break',
    'analyze_offside_trap_effectiveness', 'calculate_defensive_line_height',
    
    # Transitions
    'calculate_transition_speed', 'analyze_team_transition', 'detect_slow_transition_alert',
    'analyze_counter_attack_opportunity', 'calculate_pressing_intensity',
    
    # Runs
    'detect_depth_run_candidate', 'analyze_space_creation_movement',
    'detect_overlapping_run', 'analyze_wing_overload',
    
    # Alerts
    'generate_tactical_alerts', 'filter_alerts_by_priority', 'create_alert_summary',
    
    # Player Scores
    'calculate_tactical_score', 'calculate_physical_score', 'calculate_decision_score',
    
    # Drill Mapping
    'DrillRecommendation', 'get_drill_recommendations', 'create_training_session',
    'get_drill_by_focus_area'
]
