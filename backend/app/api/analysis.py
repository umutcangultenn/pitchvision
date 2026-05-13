from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.user import User
from app.models.analysis import Analysis, AnalysisRead
from app.models.tactical_alert import TacticalAlert, TacticalAlertRead
from app.models.training_suggestion import TrainingSuggestion, TrainingSuggestionRead
from app.auth import get_current_active_user

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{match_id}", response_model=AnalysisRead)
def get_analysis(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get analysis for a match"""
    statement = select(Analysis).where(Analysis.match_id == match_id)
    analysis = session.exec(statement).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")
    
    # Calculate progress
    progress = 0.0
    if analysis.total_frames > 0:
        progress = (analysis.processed_frames / analysis.total_frames) * 100
    
    analysis_dict = analysis.model_dump()
    analysis_dict["progress_percentage"] = progress
    
    return AnalysisRead(**analysis_dict)


@router.get("/{match_id}/alerts", response_model=List[TacticalAlertRead])
def get_tactical_alerts(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get tactical alerts for a match"""
    statement = select(TacticalAlert).where(TacticalAlert.match_id == match_id)
    alerts = session.exec(statement).all()
    return alerts


@router.get("/{match_id}/training", response_model=List[TrainingSuggestionRead])
def get_training_suggestions(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get training suggestions for a match"""
    statement = select(TrainingSuggestion).where(TrainingSuggestion.match_id == match_id)
    suggestions = session.exec(statement).all()
    return suggestions


@router.patch("/alerts/{alert_id}/review")
def review_alert(
    alert_id: int,
    coach_notes: str = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Mark alert as reviewed"""
    alert = session.get(TacticalAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Uyarı bulunamadı")
    
    alert.is_reviewed = True
    alert.reviewed_by = current_user.id
    if coach_notes:
        alert.coach_notes = coach_notes
    
    session.add(alert)
    session.commit()
    
    return {"message": "Uyarı incelendi olarak işaretlendi"}
