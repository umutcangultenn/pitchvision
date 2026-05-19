"""
Comparison Engine.

Compares EngineEvents (AI) with AnalystEvents (Human) to generate
a ComparisonResult. Core feature for learning and validation.
"""
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime

from sqlmodel import Session, select

from ..models.engine_event import EngineEvent
from ..models.analyst_event import AnalystEvent
from ..models.comparison_result import ComparisonResult
from ..config import settings
from .ai_summarizer import generate_comparison_summary

logger = logging.getLogger(__name__)


async def generate_comparison(
    session: Session,
    match_id: int,
) -> ComparisonResult:
    """
    Generate comparison between AI and Human events for a match.
    Persists and returns the ComparisonResult.
    """
    # 1. Fetch all events
    engine_events = session.exec(
        select(EngineEvent).where(EngineEvent.match_id == match_id)
    ).all()
    
    analyst_events = session.exec(
        select(AnalystEvent).where(AnalystEvent.match_id == match_id)
    ).all()
    
    # 2. Match events
    time_window = settings.COMPARISON_TIME_WINDOW_SECONDS
    matched_pairs, engine_unmatched, analyst_unmatched = _match_events(
        engine_events, analyst_events, time_window
    )
    
    # 3. Calculate statistics
    total_engine = len(engine_events)
    total_analyst = len(analyst_events)
    overlapping = len(matched_pairs)
    
    engine_only = len(engine_unmatched)
    analyst_only = len(analyst_unmatched)
    
    # Agreement ratio (Jaccard similarity style: overlap / union)
    union = total_engine + total_analyst - overlapping
    agreement_ratio = overlapping / union if union > 0 else 0.0
    
    # 4. Breakdown by type
    breakdown = _calculate_breakdown(
        engine_events, analyst_events, matched_pairs
    )
    
    # 5. Format matched pairs for storage
    pairs_data = []
    for ee, ae, dt, tm in matched_pairs:
        pairs_data.append({
            "engine_event_id": ee.id,
            "analyst_event_id": ae.id,
            "engine_type": ee.event_type,
            "analyst_type": ae.tag,
            "time_diff_seconds": round(dt, 1),
            "exact_type_match": tm
        })
        
    # 6. Create comparison object
    comparison = ComparisonResult(
        match_id=match_id,
        total_engine_events=total_engine,
        total_analyst_events=total_analyst,
        overlapping_events=overlapping,
        engine_only_events=engine_only,
        analyst_only_events=analyst_only,
        agreement_ratio=agreement_ratio,
        breakdown_by_type=breakdown,
        matched_pairs=pairs_data,
        time_window_seconds=time_window,
        created_at=datetime.utcnow()
    )
    
    # 7. Generate AI Summary (Async)
    summary_data = {
        "total_engine_events": total_engine,
        "total_analyst_events": total_analyst,
        "overlapping_events": overlapping,
        "engine_only_events": engine_only,
        "analyst_only_events": analyst_only,
        "agreement_ratio": agreement_ratio,
    }
    ai_summary = await generate_comparison_summary(summary_data)
    comparison.comparison_summary = ai_summary
    
    # 8. Clean up old comparisons for this match, then save new one
    old_comps = session.exec(
        select(ComparisonResult).where(ComparisonResult.match_id == match_id)
    ).all()
    for old in old_comps:
        session.delete(old)
        
    session.add(comparison)
    session.commit()
    session.refresh(comparison)
    
    logger.info(
        f"Generated comparison for match {match_id}: "
        f"Agreement {agreement_ratio:.2f} ({overlapping} overlaps)"
    )
    
    return comparison


def _match_events(
    engine_events: List[EngineEvent],
    analyst_events: List[AnalystEvent],
    time_window: float,
) -> Tuple[List[Tuple[EngineEvent, AnalystEvent, float, bool]], List[EngineEvent], List[AnalystEvent]]:
    """
    Match events temporally and by type.
    Returns (matched_pairs, engine_unmatched, analyst_unmatched).
    """
    matched_pairs = []
    
    # Keep track of which ones are matched
    engine_matched = set()
    analyst_matched = set()
    
    # Sort by time for easier processing
    e_events = sorted(engine_events, key=lambda e: e.timestamp_seconds)
    a_events = sorted(analyst_events, key=lambda a: a.timestamp_seconds)
    
    # Fuzzy type mapping (EngineEventType -> Analyst EventTag)
    # Allows for mapping slightly different terms that mean the same thing
    type_mapping = {
        "dangerous_attack": ["dangerous_attack", "shot", "goal"],
        "rapid_transition": ["transition", "counter_attack"],
        "transition_burst": ["transition", "counter_attack"],
        "pressure_moment": ["pressing_moment", "possession_regain"],
        "attacking_overload": ["dangerous_attack"],
        "wing_overload": ["wing_overload"],
        "compactness_issue": ["compactness_issue", "defensive_breakdown"],
        "box_entry": ["dangerous_attack", "shot"],
        "possession_loss": ["possession_loss"],
        "possession_regain": ["possession_regain"],
        "defensive_cluster": ["pressing_moment"],
        "defensive_breakdown": ["defensive_breakdown", "goal"],
        "buildup_issue": ["buildup_issue", "possession_loss"],
    }
    
    # Greedy matching logic
    for ae in a_events:
        best_match = None
        best_dt = float('inf')
        exact_type_match = False
        
        for ee in e_events:
            if ee.id in engine_matched:
                continue
                
            dt = abs(ae.timestamp_seconds - ee.timestamp_seconds)
            if dt <= time_window:
                # Check type match
                valid_types = type_mapping.get(ee.event_type, [ee.event_type])
                is_type_match = ae.tag in valid_types
                
                # If there's an explicit validation link, treat as match
                is_explicit_link = (ae.validates_engine_event_id == ee.id)
                
                if is_type_match or is_explicit_link:
                    # Prefer exact matches or closest in time
                    if dt < best_dt or (is_type_match and not exact_type_match):
                        best_match = ee
                        best_dt = dt
                        exact_type_match = is_type_match
                        
        if best_match:
            matched_pairs.append((best_match, ae, best_dt, exact_type_match))
            engine_matched.add(best_match.id)
            analyst_matched.add(ae.id)
            
    # Compile unmatched
    engine_unmatched = [e for e in engine_events if e.id not in engine_matched]
    analyst_unmatched = [a for a in analyst_events if a.id not in analyst_matched]
    
    return matched_pairs, engine_unmatched, analyst_unmatched


def _calculate_breakdown(
    engine_events: List[EngineEvent],
    analyst_events: List[AnalystEvent],
    matched_pairs: List[Tuple[EngineEvent, AnalystEvent, float, bool]],
) -> Dict[str, Dict[str, int]]:
    """Calculate per-type overlap statistics."""
    breakdown = {}
    
    # Count engine events by type
    for e in engine_events:
        t = e.event_type
        if t not in breakdown:
            breakdown[t] = {"engine": 0, "analyst": 0, "overlap": 0}
        breakdown[t]["engine"] += 1
        
    # Count analyst events by type
    for a in analyst_events:
        t = a.tag
        if t not in breakdown:
            breakdown[t] = {"engine": 0, "analyst": 0, "overlap": 0}
        breakdown[t]["analyst"] += 1
        
    # Count overlaps (crediting the analyst tag type)
    for ee, ae, _, _ in matched_pairs:
        # We count the overlap under the analyst's tag since they are human
        t = ae.tag
        if t not in breakdown:
            breakdown[t] = {"engine": 0, "analyst": 0, "overlap": 0}
        breakdown[t]["overlap"] += 1
        
    return breakdown
