"""
Event Mapper.

Converts raw StatsBomb JSON events into:
  1. StatsBombEvent ORM objects (for DB storage)
  2. Tactical metrics dicts (for analysis)
  3. TacticalAlert-compatible dicts (for the alert system)
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.models.statsbomb_event import StatsBombEvent

logger = logging.getLogger(__name__)

# StatsBomb event type names → internal category
_EVENT_CATEGORY: Dict[str, str] = {
    "Pass": "pass",
    "Shot": "shot",
    "Tackle": "defensive",
    "Interception": "defensive",
    "Pressure": "defensive",
    "Duel": "duel",
    "Clearance": "defensive",
    "Miscontrol": "error",
    "Dispossessed": "error",
    "Foul Committed": "foul",
    "Foul Won": "foul",
    "Ball Recovery": "defensive",
    "Carry": "carry",
    "Dribble": "dribble",
    "Goal Keeper": "goalkeeper",
    "Half Start": "meta",
    "Half End": "meta",
    "Starting XI": "meta",
    "Substitution": "meta",
    "Offside": "offside",
    "Error": "error",
    "50/50": "duel",
    "Bad Behaviour": "discipline",
    "Ball Receipt*": "pass",
    "Block": "defensive",
    "Camera On": "meta",
    "Camera off": "meta",
    "Injury Stoppage": "meta",
    "Player Off": "meta",
    "Player On": "meta",
    "Referee Ball-Drop": "meta",
    "Shield": "carry",
    "Tactical Shift": "meta",
}


def _parse_timestamp(ts: str) -> float:
    """Convert 'MM:SS.mmm' or 'HH:MM:SS.mmm' to seconds."""
    if not ts:
        return 0.0
    parts = ts.split(":")
    try:
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        return float(parts[0])
    except (ValueError, IndexError):
        return 0.0


class EventMapper:
    """Maps raw StatsBomb dicts to internal representations."""

    # ── DB model ──────────────────────────────────────────────────────────────

    def raw_to_db_event(
        self,
        raw: Dict[str, Any],
        match_id: int,
        statsbomb_match_id: int,
    ) -> StatsBombEvent:
        """Convert a raw StatsBomb event dict to a StatsBombEvent ORM object."""
        location = raw.get("location") or []
        ts_str = raw.get("timestamp", "00:00:00.000")

        return StatsBombEvent(
            statsbomb_id=raw["id"],
            match_id=match_id,
            statsbomb_match_id=statsbomb_match_id,
            event_index=raw.get("index", 0),
            period=raw.get("period", 1),
            timestamp_str=ts_str,
            timestamp_seconds=_parse_timestamp(ts_str),
            minute=raw.get("minute", 0),
            second=raw.get("second", 0),
            event_type=raw.get("type", {}).get("name", "Unknown"),
            possession=raw.get("possession", 0),
            possession_team_id=raw.get("possession_team", {}).get("id"),
            possession_team_name=raw.get("possession_team", {}).get("name"),
            play_pattern=raw.get("play_pattern", {}).get("name"),
            player_id=raw.get("player", {}).get("id"),
            player_name=raw.get("player", {}).get("name"),
            team_id=raw.get("team", {}).get("id"),
            team_name=raw.get("team", {}).get("name"),
            position=raw.get("position", {}).get("name"),
            location_x=location[0] if len(location) > 0 else None,
            location_y=location[1] if len(location) > 1 else None,
            duration=raw.get("duration"),
            raw_data=raw,
        )

    # ── Tactical metrics ──────────────────────────────────────────────────────

    def events_to_metrics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compute match-level tactical metrics from a list of raw StatsBomb events.
        Returns a dict compatible with the Analysis model fields.
        """
        home_id, away_id = self._detect_teams(events)

        possession = self._calc_possession(events, home_id, away_id)
        passes = self._calc_passes(events, home_id, away_id)
        shots = self._calc_shots(events, home_id, away_id)
        tackles = self._calc_by_type(events, "Tackle", home_id, away_id)
        pressures = self._calc_by_type(events, "Pressure", home_id, away_id)
        duels = self._calc_by_type(events, "Duel", home_id, away_id)
        clearances = self._calc_by_type(events, "Clearance", home_id, away_id)
        interceptions = self._calc_by_type(events, "Interception", home_id, away_id)

        return {
            "possession_home": possession["home"],
            "possession_away": possession["away"],
            "passes_completed_home": passes["home"]["completed"],
            "passes_completed_away": passes["away"]["completed"],
            "passes_attempted_home": passes["home"]["total"],
            "passes_attempted_away": passes["away"]["total"],
            "shots_home": shots["home"],
            "shots_away": shots["away"],
            "shots_on_target_home": shots["home_on_target"],
            "shots_on_target_away": shots["away_on_target"],
            "tackles_home": tackles["home"],
            "tackles_away": tackles["away"],
            "pressures_home": pressures["home"],
            "pressures_away": pressures["away"],
            "duels_home": duels["home"],
            "duels_away": duels["away"],
            "clearances_home": clearances["home"],
            "clearances_away": clearances["away"],
            "interceptions_home": interceptions["home"],
            "interceptions_away": interceptions["away"],
            "home_team_id": home_id,
            "away_team_id": away_id,
            "total_events": len(events),
        }

    # ── Alert generation ──────────────────────────────────────────────────────

    def events_to_alerts(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate tactical alert dicts from StatsBomb events.
        Compatible with the TacticalAlert model schema.
        """
        alerts: List[Dict[str, Any]] = []

        for ev in events:
            ev_type = ev.get("type", {}).get("name", "")
            ts = _parse_timestamp(ev.get("timestamp", "00:00:00.000"))
            player_id = ev.get("player", {}).get("id")
            team_id = ev.get("team", {}).get("id")

            alert = self._event_to_alert(ev_type, ts, player_id, team_id, ev)
            if alert:
                alerts.append(alert)

        return alerts

    # ── Event timeline ────────────────────────────────────────────────────────

    def events_to_timeline(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert events to a lightweight timeline format for the frontend
        EventTimeline component.
        """
        timeline = []
        for ev in events:
            ev_type = ev.get("type", {}).get("name", "")
            category = _EVENT_CATEGORY.get(ev_type, "other")

            # Only include meaningful events for the timeline
            if category == "meta":
                continue

            ts = _parse_timestamp(ev.get("timestamp", "00:00:00.000"))
            location = ev.get("location") or []

            entry: Dict[str, Any] = {
                "id": ev.get("id"),
                "type": ev_type,
                "category": category,
                "timestamp": ts,
                "minute": ev.get("minute", 0),
                "second": ev.get("second", 0),
                "period": ev.get("period", 1),
                "player_id": ev.get("player", {}).get("id"),
                "player_name": ev.get("player", {}).get("name"),
                "team_id": ev.get("team", {}).get("id"),
                "team_name": ev.get("team", {}).get("name"),
                "location_x": location[0] if len(location) > 0 else None,
                "location_y": location[1] if len(location) > 1 else None,
            }

            # Enrich with type-specific data
            if ev_type == "Pass":
                pass_data = ev.get("pass", {})
                entry["outcome"] = pass_data.get("outcome", {}).get("name", "Complete")
                entry["length"] = pass_data.get("length")
                end_loc = pass_data.get("end_location") or []
                entry["end_x"] = end_loc[0] if len(end_loc) > 0 else None
                entry["end_y"] = end_loc[1] if len(end_loc) > 1 else None

            elif ev_type == "Shot":
                shot_data = ev.get("shot", {})
                entry["outcome"] = shot_data.get("outcome", {}).get("name", "Off T")
                entry["xg"] = shot_data.get("statsbomb_xg")
                end_loc = shot_data.get("end_location") or []
                entry["end_x"] = end_loc[0] if len(end_loc) > 0 else None
                entry["end_y"] = end_loc[1] if len(end_loc) > 1 else None

            timeline.append(entry)

        return timeline

    # ── Private helpers ───────────────────────────────────────────────────────

    def _detect_teams(
        self, events: List[Dict[str, Any]]
    ) -> Tuple[Optional[int], Optional[int]]:
        """Detect home and away team IDs from events."""
        team_ids = []
        for ev in events:
            tid = ev.get("team", {}).get("id")
            if tid and tid not in team_ids:
                team_ids.append(tid)
            if len(team_ids) == 2:
                break
        home = team_ids[0] if len(team_ids) > 0 else None
        away = team_ids[1] if len(team_ids) > 1 else None
        return home, away

    def _calc_possession(
        self,
        events: List[Dict[str, Any]],
        home_id: Optional[int],
        away_id: Optional[int],
    ) -> Dict[str, float]:
        home_count = away_count = 0
        for ev in events:
            tid = ev.get("possession_team", {}).get("id")
            if tid == home_id:
                home_count += 1
            elif tid == away_id:
                away_count += 1
        total = home_count + away_count or 1
        return {
            "home": round(home_count / total * 100, 1),
            "away": round(away_count / total * 100, 1),
        }

    def _calc_passes(
        self,
        events: List[Dict[str, Any]],
        home_id: Optional[int],
        away_id: Optional[int],
    ) -> Dict[str, Dict[str, int]]:
        home = {"total": 0, "completed": 0}
        away = {"total": 0, "completed": 0}
        for ev in events:
            if ev.get("type", {}).get("name") != "Pass":
                continue
            tid = ev.get("team", {}).get("id")
            outcome = ev.get("pass", {}).get("outcome", {}).get("name")
            completed = outcome is None or outcome == "Complete"
            if tid == home_id:
                home["total"] += 1
                if completed:
                    home["completed"] += 1
            elif tid == away_id:
                away["total"] += 1
                if completed:
                    away["completed"] += 1
        return {"home": home, "away": away}

    def _calc_shots(
        self,
        events: List[Dict[str, Any]],
        home_id: Optional[int],
        away_id: Optional[int],
    ) -> Dict[str, int]:
        home = home_ot = away = away_ot = 0
        for ev in events:
            if ev.get("type", {}).get("name") != "Shot":
                continue
            tid = ev.get("team", {}).get("id")
            outcome = ev.get("shot", {}).get("outcome", {}).get("name", "")
            on_target = outcome in ("Goal", "Saved", "Saved To Post")
            if tid == home_id:
                home += 1
                if on_target:
                    home_ot += 1
            elif tid == away_id:
                away += 1
                if on_target:
                    away_ot += 1
        return {"home": home, "away": away, "home_on_target": home_ot, "away_on_target": away_ot}

    def _calc_by_type(
        self,
        events: List[Dict[str, Any]],
        event_type: str,
        home_id: Optional[int],
        away_id: Optional[int],
    ) -> Dict[str, int]:
        home = away = 0
        for ev in events:
            if ev.get("type", {}).get("name") != event_type:
                continue
            tid = ev.get("team", {}).get("id")
            if tid == home_id:
                home += 1
            elif tid == away_id:
                away += 1
        return {"home": home, "away": away}

    def _event_to_alert(
        self,
        ev_type: str,
        ts: float,
        player_id: Optional[int],
        team_id: Optional[int],
        raw: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Map a single event to an alert dict, or None if not alertable."""
        base = {
            "timestamp_seconds": ts,
            "player_id": player_id,
            "team_id": team_id,
            "is_reviewed": False,
        }

        if ev_type == "Error":
            return {**base, "category": "Savunma", "severity": "warning",
                    "title": "Top Kaybı (Hata)", "description": "Oyuncu hatası nedeniyle top kaybedildi."}

        if ev_type == "Miscontrol":
            return {**base, "category": "Top Hakimiyeti", "severity": "info",
                    "title": "Top Kontrolü Kaybı", "description": "Oyuncu topu kontrol edemedi."}

        if ev_type == "Dispossessed":
            return {**base, "category": "Savunma", "severity": "warning",
                    "title": "Top Çalındı", "description": "Rakip oyuncu topu ele geçirdi."}

        if ev_type == "Shot":
            outcome = raw.get("shot", {}).get("outcome", {}).get("name", "")
            if outcome == "Goal":
                return {**base, "category": "Hücum", "severity": "info",
                        "title": "Gol", "description": "Gol kaydedildi."}
            if outcome in ("Saved", "Saved To Post"):
                return {**base, "category": "Hücum", "severity": "info",
                        "title": "Kurtarış", "description": f"Şut kurtarıldı ({outcome})."}

        if ev_type == "Foul Committed":
            return {**base, "category": "Savunma", "severity": "info",
                    "title": "Faul", "description": "Faul yapıldı."}

        return None
