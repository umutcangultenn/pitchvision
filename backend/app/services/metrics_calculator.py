"""
Advanced Metrics Calculator.

Computes xG, xA, PPDA, progressive passes, field tilt, and other
advanced metrics from StatsBomb event data.
"""
import logging
import math
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# StatsBomb pitch dimensions
_PITCH_LENGTH = 120.0  # yards (StatsBomb uses yards)
_PITCH_WIDTH = 80.0
_GOAL_X = 120.0
_GOAL_Y = 40.0


class MetricsCalculator:
    """Calculate advanced football metrics from StatsBomb events."""

    # ── xG ────────────────────────────────────────────────────────────────────

    def calculate_xg(
        self, events: List[Dict[str, Any]], team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Extract xG values from StatsBomb shot events.
        StatsBomb provides statsbomb_xg directly on shot events.
        """
        shots = [
            ev for ev in events
            if ev.get("type", {}).get("name") == "Shot"
            and (team_id is None or ev.get("team", {}).get("id") == team_id)
        ]

        total_xg = 0.0
        shot_details = []

        for shot in shots:
            shot_data = shot.get("shot", {})
            xg = shot_data.get("statsbomb_xg", 0.0) or 0.0
            total_xg += xg

            location = shot.get("location") or []
            shot_details.append({
                "player": shot.get("player", {}).get("name"),
                "minute": shot.get("minute", 0),
                "xg": round(xg, 4),
                "outcome": shot_data.get("outcome", {}).get("name", "Unknown"),
                "technique": shot_data.get("technique", {}).get("name"),
                "body_part": shot_data.get("body_part", {}).get("name"),
                "location_x": location[0] if len(location) > 0 else None,
                "location_y": location[1] if len(location) > 1 else None,
            })

        return {
            "total_xg": round(total_xg, 3),
            "shot_count": len(shots),
            "shots": shot_details,
            "xg_per_shot": round(total_xg / len(shots), 4) if shots else 0.0,
        }

    # ── PPDA ─────────────────────────────────────────────────────────────────

    def calculate_ppda(
        self,
        events: List[Dict[str, Any]],
        home_id: Optional[int],
        away_id: Optional[int],
    ) -> Dict[str, float]:
        """
        PPDA = Passes Allowed Per Defensive Action.
        Lower PPDA = more intense pressing.
        Calculated in the opponent's half (x > 60 for StatsBomb coords).
        """
        home_passes_allowed = 0
        home_def_actions = 0
        away_passes_allowed = 0
        away_def_actions = 0

        defensive_types = {"Tackle", "Interception", "Pressure", "Foul Committed", "Block"}

        for ev in events:
            ev_type = ev.get("type", {}).get("name", "")
            team_id = ev.get("team", {}).get("id")
            location = ev.get("location") or []
            x = location[0] if len(location) > 0 else 0

            # Home team pressing (in away half: x > 60)
            if team_id == home_id and x > 60:
                if ev_type == "Pass":
                    away_passes_allowed += 1
                elif ev_type in defensive_types:
                    home_def_actions += 1

            # Away team pressing (in home half: x < 60)
            elif team_id == away_id and x < 60:
                if ev_type == "Pass":
                    home_passes_allowed += 1
                elif ev_type in defensive_types:
                    away_def_actions += 1

        home_ppda = round(home_passes_allowed / home_def_actions, 2) if home_def_actions > 0 else 99.0
        away_ppda = round(away_passes_allowed / away_def_actions, 2) if away_def_actions > 0 else 99.0

        return {
            "home_ppda": home_ppda,
            "away_ppda": away_ppda,
            "home_def_actions": home_def_actions,
            "away_def_actions": away_def_actions,
        }

    # ── Progressive passes ────────────────────────────────────────────────────

    def calculate_progressive_passes(
        self,
        events: List[Dict[str, Any]],
        team_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Progressive pass: a completed pass that moves the ball at least
        10 yards closer to the opponent's goal (StatsBomb definition).
        """
        passes = [
            ev for ev in events
            if ev.get("type", {}).get("name") == "Pass"
            and (team_id is None or ev.get("team", {}).get("id") == team_id)
        ]

        progressive = []
        for p in passes:
            outcome = p.get("pass", {}).get("outcome", {}).get("name")
            if outcome and outcome != "Complete":
                continue  # incomplete pass

            start = p.get("location") or []
            end = p.get("pass", {}).get("end_location") or []

            if len(start) < 2 or len(end) < 2:
                continue

            # Distance from goal before and after
            dist_before = self._dist_to_goal(start[0], start[1])
            dist_after = self._dist_to_goal(end[0], end[1])

            if dist_before - dist_after >= 10:  # 10 yards closer to goal
                progressive.append({
                    "player": p.get("player", {}).get("name"),
                    "minute": p.get("minute", 0),
                    "start_x": start[0],
                    "start_y": start[1],
                    "end_x": end[0],
                    "end_y": end[1],
                    "distance_gained": round(dist_before - dist_after, 1),
                })

        return {
            "total_progressive_passes": len(progressive),
            "total_passes": len(passes),
            "progressive_pass_rate": round(len(progressive) / len(passes) * 100, 1) if passes else 0.0,
            "progressive_passes": progressive,
        }

    # ── Field tilt ────────────────────────────────────────────────────────────

    def calculate_field_tilt(
        self,
        events: List[Dict[str, Any]],
        home_id: Optional[int],
        away_id: Optional[int],
    ) -> Dict[str, float]:
        """
        Field tilt = % of touches in the final third (x > 80).
        Measures territorial dominance in the attacking third.
        """
        touch_types = {"Pass", "Shot", "Carry", "Dribble", "Ball Receipt*", "Miscontrol"}

        home_final_third = 0
        away_final_third = 0

        for ev in events:
            ev_type = ev.get("type", {}).get("name", "")
            if ev_type not in touch_types:
                continue

            team_id = ev.get("team", {}).get("id")
            location = ev.get("location") or []
            x = location[0] if len(location) > 0 else 0

            if team_id == home_id and x > 80:
                home_final_third += 1
            elif team_id == away_id and x < 40:  # away's attacking third
                away_final_third += 1

        total = home_final_third + away_final_third or 1
        return {
            "home_field_tilt": round(home_final_third / total * 100, 1),
            "away_field_tilt": round(away_final_third / total * 100, 1),
            "home_final_third_touches": home_final_third,
            "away_final_third_touches": away_final_third,
        }

    # ── Player-level metrics ──────────────────────────────────────────────────

    def calculate_player_metrics(
        self, events: List[Dict[str, Any]], player_id: int
    ) -> Dict[str, Any]:
        """Aggregate metrics for a single player."""
        player_events = [
            ev for ev in events
            if ev.get("player", {}).get("id") == player_id
        ]

        passes = [ev for ev in player_events if ev.get("type", {}).get("name") == "Pass"]
        shots = [ev for ev in player_events if ev.get("type", {}).get("name") == "Shot"]
        tackles = [ev for ev in player_events if ev.get("type", {}).get("name") == "Tackle"]
        pressures = [ev for ev in player_events if ev.get("type", {}).get("name") == "Pressure"]
        carries = [ev for ev in player_events if ev.get("type", {}).get("name") == "Carry"]
        dribbles = [ev for ev in player_events if ev.get("type", {}).get("name") == "Dribble"]

        completed_passes = [
            p for p in passes
            if p.get("pass", {}).get("outcome", {}).get("name") in (None, "Complete")
        ]

        total_xg = sum(
            s.get("shot", {}).get("statsbomb_xg", 0.0) or 0.0 for s in shots
        )

        successful_dribbles = [
            d for d in dribbles
            if d.get("dribble", {}).get("outcome", {}).get("name") == "Complete"
        ]

        player_name = player_events[0].get("player", {}).get("name") if player_events else "Unknown"

        return {
            "player_id": player_id,
            "player_name": player_name,
            "total_events": len(player_events),
            "passes_attempted": len(passes),
            "passes_completed": len(completed_passes),
            "pass_accuracy": round(len(completed_passes) / len(passes) * 100, 1) if passes else 0.0,
            "shots": len(shots),
            "xg": round(total_xg, 3),
            "tackles": len(tackles),
            "pressures": len(pressures),
            "carries": len(carries),
            "dribbles_attempted": len(dribbles),
            "dribbles_completed": len(successful_dribbles),
            "dribble_success_rate": round(len(successful_dribbles) / len(dribbles) * 100, 1) if dribbles else 0.0,
        }

    # ── Full match summary ────────────────────────────────────────────────────

    def calculate_all(
        self,
        events: List[Dict[str, Any]],
        home_id: Optional[int],
        away_id: Optional[int],
    ) -> Dict[str, Any]:
        """Compute all advanced metrics in one call."""
        return {
            "xg": {
                "home": self.calculate_xg(events, home_id),
                "away": self.calculate_xg(events, away_id),
            },
            "ppda": self.calculate_ppda(events, home_id, away_id),
            "progressive_passes": {
                "home": self.calculate_progressive_passes(events, home_id),
                "away": self.calculate_progressive_passes(events, away_id),
            },
            "field_tilt": self.calculate_field_tilt(events, home_id, away_id),
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _dist_to_goal(self, x: float, y: float) -> float:
        """Euclidean distance from (x, y) to the attacking goal centre."""
        return math.sqrt((x - _GOAL_X) ** 2 + (y - _GOAL_Y) ** 2)
