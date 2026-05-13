from fastapi import APIRouter, status

from app.schemas.saas import DemoRequestCreate, DemoRequestResponse
from app.services import api_service

router = APIRouter(tags=["saas"])


@router.post(
    "/demo-requests",
    response_model=DemoRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_demo_request(payload: DemoRequestCreate) -> DemoRequestResponse:
    """Demo / satış talebi (MVP: kuyruk simülasyonu)."""
    return api_service.submit_demo_request(payload)
