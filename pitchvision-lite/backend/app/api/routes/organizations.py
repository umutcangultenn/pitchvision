from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.organization import OrganizationRead, OrganizationUpdate
from app.services import api_service

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/me", response_model=OrganizationRead)
def get_my_org(
    current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> OrganizationRead:
    return api_service.get_org(session, current_user.organization_id)


@router.patch("/me", response_model=OrganizationRead)
def patch_my_org(
    payload: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> OrganizationRead:
    return api_service.update_org(session, current_user.organization_id, payload)
