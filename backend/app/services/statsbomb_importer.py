"""
StatsBomb Importer.

Imports StatsBomb open-data events into the local database, linking them
to existing Match records (or creating placeholder matches when needed).

Usage:
    from app.services.statsbomb_importer import StatsBombImporter
    from app.database import get_session

    with Session(engine) as session:
        importer = StatsBombImporter(session)
        result = importer.import_match(statsbomb_match_id=3788741, team_id=1)
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlmodel import Session, select

from app.models.match import Match, MatchStatus
from app.models.statsbomb_event import StatsBombEvent
from app.services.statsbomb_loader import StatsBombLoader
from app.services.event_mapper import EventMapper

logger = logging.getLogger(__name__)


class ImportResult:
    """Summary of a single import operation."""

    def __init__(self, statsbomb_match_id: int):
        self.statsbomb_match_id = statsbomb_match_id
        self.match_id: Optional[int] = None
        self.events_imported: int = 0
        self.events_skipped: int = 0
        self.errors: List[str] = []
        self.success: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statsbomb_match_id": self.statsbomb_match_id,
            "match_id": self.match_id,
            "events_imported": self.events_imported,
            "events_skipped": self.events_skipped,
            "errors": self.errors,
            "success": self.success,
        }


class StatsBombImporter:
    """Imports StatsBomb data into the PitchVision database."""

    def __init__(self, session: Session, loader: Optional[StatsBombLoader] = None):
        self.session = session
        self.loader = loader or StatsBombLoader()
        self.mapper = EventMapper()

    # ── Public API ────────────────────────────────────────────────────────────

    def import_match(
        self,
        statsbomb_match_id: int,
        team_id: int,
        match_id: Optional[int] = None,
        skip_existing: bool = True,
    ) -> ImportResult:
        """
        Import all events for a StatsBomb match.

        Args:
            statsbomb_match_id: The StatsBomb match_id (e.g. 3788741).
            team_id: The local team_id to associate the match with.
            match_id: If provided, link events to this existing Match record.
                      If None, a new Match record is created.
            skip_existing: If True, skip if events already exist for this
                           statsbomb_match_id.

        Returns:
            ImportResult with counts and any errors.
        """
        result = ImportResult(statsbomb_match_id)

        # Check for existing events
        if skip_existing:
            existing = self.session.exec(
                select(StatsBombEvent).where(
                    StatsBombEvent.statsbomb_match_id == statsbomb_match_id
                ).limit(1)
            ).first()
            if existing:
                logger.info("Events already exist for statsbomb_match_id=%s, skipping", statsbomb_match_id)
                result.match_id = existing.match_id
                result.success = True
                result.events_skipped = -1  # sentinel: already imported
                return result

        # Fetch raw events
        try:
            raw_events = self.loader.get_events(statsbomb_match_id)
        except Exception as exc:
            result.errors.append(f"Failed to fetch events: {exc}")
            return result

        if not raw_events:
            result.errors.append("No events returned from StatsBomb")
            return result

        # Resolve or create Match record
        if match_id is None:
            match_id = self._create_match_from_events(raw_events, team_id, statsbomb_match_id)

        result.match_id = match_id

        # Import events in bulk
        db_events: List[StatsBombEvent] = []
        for raw in raw_events:
            try:
                ev = self.mapper.raw_to_db_event(raw, match_id, statsbomb_match_id)
                db_events.append(ev)
            except Exception as exc:
                result.events_skipped += 1
                logger.debug("Skipping event %s: %s", raw.get("id"), exc)

        # Bulk insert
        try:
            self.session.add_all(db_events)
            self.session.commit()
            result.events_imported = len(db_events)
            result.success = True
            logger.info(
                "Imported %d events for statsbomb_match_id=%s → match_id=%s",
                len(db_events), statsbomb_match_id, match_id,
            )
        except Exception as exc:
            self.session.rollback()
            result.errors.append(f"DB insert failed: {exc}")

        return result

    def import_competition(
        self,
        competition_id: int,
        season_id: int,
        team_id: int,
        max_matches: Optional[int] = None,
    ) -> List[ImportResult]:
        """
        Import all matches for a competition/season.

        Args:
            competition_id: StatsBomb competition_id (e.g. 11 = La Liga).
            season_id: StatsBomb season_id.
            team_id: Local team_id to associate matches with.
            max_matches: Limit number of matches imported (useful for testing).

        Returns:
            List of ImportResult, one per match.
        """
        try:
            matches = self.loader.get_matches(competition_id, season_id)
        except Exception as exc:
            logger.error("Failed to fetch matches for comp=%s season=%s: %s", competition_id, season_id, exc)
            return []

        if max_matches:
            matches = matches[:max_matches]

        results: List[ImportResult] = []
        for match_data in matches:
            sb_match_id = match_data["match_id"]
            logger.info("Importing match %s (%s vs %s)", sb_match_id,
                        match_data.get("home_team", {}).get("home_team_name", "?"),
                        match_data.get("away_team", {}).get("away_team_name", "?"))
            result = self.import_match(sb_match_id, team_id)
            results.append(result)

        return results

    # ── Internal ──────────────────────────────────────────────────────────────

    def _create_match_from_events(
        self,
        raw_events: List[Dict[str, Any]],
        team_id: int,
        statsbomb_match_id: int,
    ) -> int:
        """Create a Match record from StatsBomb event metadata."""
        # Extract team names from first event
        home_team = "Home Team"
        away_team = "Away Team"
        for ev in raw_events:
            pt = ev.get("possession_team", {})
            if pt:
                home_team = pt.get("name", home_team)
                break

        match = Match(
            team_id=team_id,
            opponent_name=away_team,
            match_date=datetime.utcnow(),
            location="StatsBomb Import",
            home_away="Ev Sahibi",
            status=MatchStatus.COMPLETED,
            notes=f"Imported from StatsBomb match_id={statsbomb_match_id}",
        )
        self.session.add(match)
        self.session.commit()
        self.session.refresh(match)
        return match.id
