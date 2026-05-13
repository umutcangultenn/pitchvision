"""
Match report API endpoints.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ..reports.match_report import generate_match_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


class GenerateReportRequest(BaseModel):
    match_id: int
    match_data: Dict[str, Any]
    alerts: List[Dict[str, Any]] = []
    clips: List[Dict[str, Any]] = []
    players: List[Dict[str, Any]] = []
    performances: List[Dict[str, Any]] = []
    team_shape: Optional[Dict[str, Any]] = None


@router.post("/generate")
async def generate_report(req: GenerateReportRequest):
    """Maç raporu oluşturur ve JSON olarak döner."""
    try:
        report = generate_match_report(
            match_id=req.match_id,
            match_data=req.match_data,
            alerts_data=req.alerts,
            clips_data=req.clips,
            players_data=req.players,
            performances_data=req.performances,
            team_shape_data=req.team_shape,
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/html", response_class=HTMLResponse)
async def generate_report_html(req: GenerateReportRequest):
    """Maç raporunu PDF'e uygun HTML olarak döner."""
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "templates"))
        from pdf_export import render_report_html  # type: ignore

        report = generate_match_report(
            match_id=req.match_id,
            match_data=req.match_data,
            alerts_data=req.alerts,
            clips_data=req.clips,
            players_data=req.players,
            performances_data=req.performances,
            team_shape_data=req.team_shape,
        )
        html = render_report_html(report.to_dict())
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo/{match_id}")
async def get_demo_report(match_id: int):
    """Demo maç raporu döner (frontend geliştirme için)."""
    from ..data.demo_report import DEMO_REPORT_DATA
    report = generate_match_report(**DEMO_REPORT_DATA, match_id=match_id)
    return report.to_dict()
