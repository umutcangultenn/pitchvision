from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.models.match_report import MatchReport, MatchReportRead
from app.auth import get_current_active_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{match_id}", response_model=MatchReportRead)
def get_match_report(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get match report"""
    statement = select(MatchReport).where(MatchReport.match_id == match_id)
    report = session.exec(statement).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı")
    
    return report
