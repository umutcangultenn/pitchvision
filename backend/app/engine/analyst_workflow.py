"""
Module 4 — Manual Analyst Workflow.

Service layer for the human analyst workflow (Flow B).
Provides methods to create, update, and manage manual event tags,
and to validate/review AI-detected engine events.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from sqlmodel import Session, select

from ..models.analyst_event import AnalystEvent, AnalystEventCreate, AnalystEventUpdate, ValidationStatus
from ..models.engine_event import EngineEvent, AnalystVerdict
from ..models.match_segment import MatchSegment
from ..engine.segmentation import assign_event_to_segment

logger = logging.getLogger(__name__)


def create_analyst_event(
    session: Session,
    event_in: AnalystEventCreate,
    analyst_id: int,
    segments: List[MatchSegment],
) -> AnalystEvent:
    """
    Create a new manual analyst event.
    Optionally links to an EngineEvent if validating/rejecting it.
    """
    # Assign to segment if not explicitly provided
    segment_id = event_in.segment_id
    if not segment_id and segments:
        seg = assign_event_to_segment(segments, event_in.timestamp_seconds)
        if seg:
            segment_id = seg.id

    db_event = AnalystEvent(
        match_id=event_in.match_id,
        segment_id=segment_id,
        analyst_id=analyst_id,
        tag=event_in.tag,
        timestamp_seconds=event_in.timestamp_seconds,
        notes=event_in.notes,
        confidence=event_in.confidence,
        validates_engine_event_id=event_in.validates_engine_event_id,
        validation_status=event_in.validation_status,
        metadata=event_in.metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    
    # If this validates an engine event, update the engine event too
    if event_in.validates_engine_event_id and event_in.validation_status:
        review_engine_event(
            session=session,
            engine_event_id=event_in.validates_engine_event_id,
            analyst_id=analyst_id,
            verdict=AnalystVerdict(event_in.validation_status),
            notes=event_in.notes,
        )

    logger.info(f"Analyst {analyst_id} created event {db_event.id} ({db_event.tag})")
    return db_event


def update_analyst_event(
    session: Session,
    event_id: int,
    event_in: AnalystEventUpdate,
    analyst_id: int,
) -> Optional[AnalystEvent]:
    """Update an existing analyst event."""
    db_event = session.get(AnalystEvent, event_id)
    if not db_event:
        return None
        
    # Only allow the creator to update (or an admin - simplified here)
    if db_event.analyst_id != analyst_id:
        raise ValueError("Not authorized to update this event")

    update_data = event_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
        
    db_event.updated_at = datetime.utcnow()
    
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    
    # Update linked engine event if validation status changed
    if db_event.validates_engine_event_id and "validation_status" in update_data:
        verdict_str = update_data["validation_status"]
        if verdict_str:
            review_engine_event(
                session=session,
                engine_event_id=db_event.validates_engine_event_id,
                analyst_id=analyst_id,
                verdict=AnalystVerdict(verdict_str),
                notes=db_event.notes,
            )
            
    return db_event


def get_analyst_events_for_match(
    session: Session,
    match_id: int,
) -> List[AnalystEvent]:
    """Get all analyst events for a given match."""
    statement = select(AnalystEvent).where(
        AnalystEvent.match_id == match_id
    ).order_by(AnalystEvent.timestamp_seconds)
    
    return list(session.exec(statement).all())


def review_engine_event(
    session: Session,
    engine_event_id: int,
    analyst_id: int,
    verdict: AnalystVerdict,
    notes: Optional[str] = None,
) -> Optional[EngineEvent]:
    """
    Directly review/validate an AI-detected engine event.
    Updates the EngineEvent record.
    """
    engine_event = session.get(EngineEvent, engine_event_id)
    if not engine_event:
        return None
        
    engine_event.analyst_reviewed = True
    engine_event.analyst_verdict = verdict.value
    engine_event.reviewed_by = analyst_id
    engine_event.reviewed_at = datetime.utcnow()
    
    if notes is not None:
        engine_event.analyst_notes = notes
        
    session.add(engine_event)
    session.commit()
    session.refresh(engine_event)
    
    logger.info(
        f"Analyst {analyst_id} reviewed EngineEvent {engine_event_id} "
        f"with verdict: {verdict.value}"
    )
    
    return engine_event


def save_analyst_segment_summary(
    session: Session,
    segment_id: int,
    analyst_id: int,
    summary_text: str,
) -> Optional[MatchSegment]:
    """Save an analyst's manual summary for a specific segment."""
    segment = session.get(MatchSegment, segment_id)
    if not segment:
        return None
        
    segment.analyst_summary = summary_text
    segment.updated_at = datetime.utcnow()
    
    session.add(segment)
    session.commit()
    session.refresh(segment)
    
    return segment
