"""
StatsBomb API endpoints.

Provides access to StatsBomb open-data competitions, matches, events,
and computed metrics/alerts without requiring a database import step.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select

from app.database import get_session
from app.auth import get_current_active_user
from app.models.user import User
from app.models.statsbomb_event import StatsBombEvent, StatsBombEventRead
from app.services.statsbomb_loader import StatsBombLoader
from app.services.event_mapper import EventMapper
from app.services.metrics_calculator import MetricsCalculator
from app.services.statsbomb_importer import StatsBombImporter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statsbomb", tags=["statsbomb"])

# Shared service instances (stateless, safe to reuse)
_loader = StatsBombLoader()
_mapper = EventMapper()
_calc = MetricsCalculator()


# ── Competitions & Matches ────────────────────────────────────────────────────

@router.get("/competitions", response_model=List[Dict[str, Any]])
def get_competitions(
    current_user: User = Depends(get_current_active_user),
):
    """Return all available StatsBomb competitions."""
    try:
        return _loader.get_competitions()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"StatsBomb fetch failed: {exc}")


@router.get("/matches/{competition_id}", response_model=List[Dict[str, Any]])
def get_matches(
    competition_id: int,
    season_id: Optional[int] = Query(None, description="Filter by season ID"),
    current_user: User = Depends(get_current_active_user),
):
    """Return matches for a competition, optionally filtered by season."""
    try:
        return _loader.get_matches(competition_id, season_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"StatsBomb fetch failed: {exc}")


# ── Events ────────────────────────────────────────────────────────────────────

@router.get("/events/{statsbomb_match_id}", response_model=List[Dict[str, Any]])
def get_raw_events(
    statsbomb_match_id: int,
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. 'Pass', 'Shot')"),
    current_user: User = Depends(get_current_active_user),
):
    """Return raw StatsBomb events for a match, optionally filtered by type."""
    try:
        events = _loader.get_events(statsbomb_match_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"StatsBomb fetch failed: {exc}")

    if event_type:
        events = [e for e in events if e.get("type", {}).get("name", "").lower() == event_type.lower()]

    return events


@router.get("/timeline/{statsbomb_match_id}", response_model=List[Dict[str, Any]])
def get_event_timeline(
    statsbomb_match_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Return a lightweight event timeline for the frontend EventTimeline component.
    Filters out meta events (kick-off, half-start, etc.).
    """
    try:
        events = _loader.get_events(statsbomb_match_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"StatsBomb fetch failed: {exc}")

    return _mapper.events_to_timeline(events)


# ── Metrics ───────────────────────────────────────────────────────────────────

@router.get("/metrics/{statsbomb_match_id}", response_model=Dict[str, Any])
def get_match_metrics(
    statsbomb_match_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Compute basic tactical metrics (possession, passes, shots, etc.)
    from StatsBomb events.
    """
    try:
        events = _loader.get_events(statsbomb_match_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"StatsBomb fetch failed: {exc}")

    return _mapper.events_to_metrics(events)


@router.get("/advanced-metrics/{statsbomb_match_id}", response_model=Dict[str, Any])
def get_advanced_metrics(
    statsbomb_match_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Compute advanced metrics: xG, PPDA, progressive passes, field tilt.
    """
    try:
        events = _loader.get_events(statsbomb_match_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"StatsBomb fetch failed: {exc}")

    basic = _mapper.events_to_metrics(events)
    home_id = basic.get("home_team_id")
    away_id = basic.get("away_team_id")

    advanced = _calc.calculate_all(events, home_id, away_id)
    return {**basic, "advanced": advanced}


@router.get("/player-metrics/{statsbomb_match_id}/{player_id}", response_model=Dict[str, Any])
def get_player_metrics(
    statsbomb_match_id: int,
    player_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Compute per-player advanced metrics for a specific match."""
    try:
        events = _loader.get_events(statsbomb_match_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"StatsBomb fetch failed: {exc}")

    return _calc.calculate_player_metrics(events, player_id)


# ── Alerts ────────────────────────────────────────────────────────────────────

@router.get("/alerts/{statsbomb_match_id}", response_model=List[Dict[str, Any]])
def get_match_alerts(
    statsbomb_match_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate tactical alerts from StatsBomb events.
    Returns alert dicts compatible with the TacticalAlert schema.
    """
    try:
        events = _loader.get_events(statsbomb_match_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"StatsBomb fetch failed: {exc}")

    return _mapper.events_to_alerts(events)


# ── Import ────────────────────────────────────────────────────────────────────

@router.post("/import/{statsbomb_match_id}", response_model=Dict[str, Any])
def import_match(
    statsbomb_match_id: int,
    team_id: int = Query(..., description="Local team_id to associate the match with"),
    match_id: Optional[int] = Query(None, description="Existing match_id to link events to"),
    skip_existing: bool = Query(True, description="Skip if events already imported"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Import StatsBomb events for a match into the local database.
    Creates a new Match record if match_id is not provided.
    """
    importer = StatsBombImporter(session, _loader)
    result = importer.import_match(
        statsbomb_match_id=statsbomb_match_id,
        team_id=team_id,
        match_id=match_id,
        skip_existing=skip_existing,
    )
    if not result.success and result.errors:
        raise HTTPException(status_code=500, detail="; ".join(result.errors))
    return result.to_dict()


@router.post("/import-competition", response_model=List[Dict[str, Any]])
def import_competition(
    competition_id: int = Query(...),
    season_id: int = Query(...),
    team_id: int = Query(...),
    max_matches: Optional[int] = Query(None, description="Limit number of matches (for testing)"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Bulk-import all matches for a competition/season.
    This can take several minutes for large competitions.
    """
    importer = StatsBombImporter(session, _loader)
    results = importer.import_competition(competition_id, season_id, team_id, max_matches)
    return [r.to_dict() for r in results]


# ── DB-backed event queries ───────────────────────────────────────────────────

@router.get("/db/events/{match_id}", response_model=List[StatsBombEventRead])
def get_db_events(
    match_id: int,
    event_type: Optional[str] = Query(None),
    limit: int = Query(500, le=5000),
    offset: int = Query(0),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Return StatsBomb events stored in the local database for a match.
    Use this after importing with /import/{statsbomb_match_id}.
    """
    stmt = select(StatsBombEvent).where(StatsBombEvent.match_id == match_id)
    if event_type:
        stmt = stmt.where(StatsBombEvent.event_type == event_type)
    stmt = stmt.order_by(StatsBombEvent.event_index).offset(offset).limit(limit)
    return session.exec(stmt).all()


@router.get("/db/events/{match_id}/count", response_model=Dict[str, Any])
def count_db_events(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Return event counts grouped by type for a match."""
    events = session.exec(
        select(StatsBombEvent).where(StatsBombEvent.match_id == match_id)
    ).all()

    counts: Dict[str, int] = {}
    for ev in events:
        counts[ev.event_type] = counts.get(ev.event_type, 0) + 1

    return {
        "match_id": match_id,
        "total": len(events),
        "by_type": dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)),
    }
