from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.enums import ReportType
from app.schemas.common_api import DictResponse
from app.schemas.report import ReportCreate, ReportRead
from app.services import api_service

router = APIRouter(tags=["reports"])


@router.get("/reports", response_model=list[ReportRead])
def list_reports(session: Session = Depends(get_session)) -> list[ReportRead]:
    return api_service.list_reports(session)


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(report_id: int, session: Session = Depends(get_session)) -> ReportRead:
    return api_service.get_report(session, report_id)


@router.post("/matches/{match_id}/report", response_model=ReportRead)
def create_match_report(match_id: int, session: Session = Depends(get_session)) -> ReportRead:
    payload = ReportCreate(
        match_id=match_id,
        player_id=None,
        report_type=ReportType.MATCH_SUMMARY,
        title=f"Match {match_id} raporu",
        summary="Otomatik oluşturulan rapor",
        html_path=f"reports/{match_id}.html",
    )
    return api_service.create_report(session, payload)


@router.get("/matches/{match_id}/report", response_model=ReportRead)
def get_match_report(match_id: int, session: Session = Depends(get_session)) -> ReportRead:
    item = api_service.match_report(session, match_id)
    if not item:
        raise api_service._not_found("Maç raporu")
    return item


@router.post("/reports/{report_id}/export-pdf", response_model=DictResponse)
def export_pdf(report_id: int, session: Session = Depends(get_session)) -> DictResponse:
    report = api_service.export_report_pdf(session, report_id)
    return DictResponse(data={"pdf_path": report.pdf_path})
