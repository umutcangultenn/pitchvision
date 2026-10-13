from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.models.enums import ReportType
from app.schemas.common_api import DictResponse
from app.schemas.report import ReportCreate, ReportRead
from app.services import api_service
from app.services.access_control import assert_org_access, require_analyst_or_above

router = APIRouter(tags=["reports"])


@router.get("/reports", response_model=list[ReportRead])
def list_reports(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> list[ReportRead]:
    return api_service.list_reports(session, current_user.organization_id)


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(
    report_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> ReportRead:
    report = api_service.get_report(session, report_id)
    match = api_service.get_match(session, report.match_id)
    assert_org_access(match.organization_id, current_user)
    return report


@router.post("/matches/{match_id}/report", response_model=ReportRead)
def create_match_report(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> ReportRead:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    require_analyst_or_above(current_user)
    
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
def get_match_report(
    match_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> ReportRead:
    match = api_service.get_match(session, match_id)
    assert_org_access(match.organization_id, current_user)
    
    item = api_service.match_report(session, match_id)
    if not item:
        raise api_service._not_found("Maç raporu")
    return item


@router.post("/reports/{report_id}/export-pdf", response_model=DictResponse)
def export_pdf(
    report_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> DictResponse:
    report_obj = api_service.get_report(session, report_id)
    match = api_service.get_match(session, report_obj.match_id)
    assert_org_access(match.organization_id, current_user)
    
    report = api_service.export_report_pdf(session, report_id)
    return DictResponse(data={"pdf_path": report.pdf_path})
