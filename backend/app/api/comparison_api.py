"""
Comparison API endpoints.
Provides endpoints for AI vs Human analyst comparison.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..auth import get_current_active_user
from ..models.user import User
from ..models.comparison_result import ComparisonResult, ComparisonResultRead, ComparisonDetailRead
from ..engine.comparison import generate_comparison

router = APIRouter(prefix="/comparison", tags=["comparison"])


@router.post("/{match_id}/generate", response_model=ComparisonResultRead)
async def generate_match_comparison(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Generate or regenerate AI vs Human comparison for a match."""
    try:
        comparison = await generate_comparison(session, match_id)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Karşılaştırma oluşturulamadı: {str(e)}")


@router.get("/{match_id}", response_model=ComparisonResultRead)
def get_comparison(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get the latest comparison results for a match."""
    comparison = session.exec(
        select(ComparisonResult)
        .where(ComparisonResult.match_id == match_id)
        .order_by(ComparisonResult.created_at.desc())
    ).first()
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Bu maç için karşılaştırma henüz oluşturulmadı")
        
    return comparison


@router.get("/{match_id}/details", response_model=ComparisonDetailRead)
def get_comparison_details(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed comparison results including matched pairs."""
    comparison = session.exec(
        select(ComparisonResult)
        .where(ComparisonResult.match_id == match_id)
        .order_by(ComparisonResult.created_at.desc())
    ).first()
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Bu maç için karşılaştırma henüz oluşturulmadı")
        
    return comparison
