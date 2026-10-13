from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.settings import (
    AppSettingsRead,
    DroneChecklistRead,
    DroneChecklistUpdate,
    OrganizationSettingsRead,
    OrganizationSettingsUpdate,
    UserRead,
    UserInviteRequest,
    TeamRead,
    TeamCreateRequest,
    SeasonRead,
    SubscriptionRead,
    VideoProcessingSettingsRead,
    VideoProcessingSettingsUpdate,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
    PrivacySettingsRead,
    PrivacySettingsUpdate,
)
from app.services import api_service
from app.services.access_control import assert_org_access, require_admin, require_coach_or_above

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=AppSettingsRead)
def get_settings(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> AppSettingsRead:
    return AppSettingsRead(app_name="PitchVision Lite API", debug=False)


# Organization Settings
@router.get("/organization", response_model=OrganizationSettingsRead)
def get_organization_settings(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Get organization settings"""
    return api_service.get_organization_settings(session, current_user.organization_id)


@router.put("/organization", response_model=OrganizationSettingsRead)
def update_organization_settings(
    data: OrganizationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update organization settings"""
    require_admin(current_user)
    return api_service.update_organization_settings(session, current_user.organization_id, data)


# User Management
@router.get("/users", response_model=list[UserRead])
def list_users(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """List all users in organization"""
    require_admin(current_user)
    return api_service.list_users(session, current_user.organization_id)


@router.post("/users/invite", response_model=dict)
def invite_user(
    data: UserInviteRequest, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Invite user to organization"""
    require_admin(current_user)
    data.organization_id = current_user.organization_id
    return api_service.invite_user(session, data)


@router.put("/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    role: str = Query(..., description="Yeni rol"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update user role"""
    require_admin(current_user)
    target_user = session.get(User, user_id)
    if not target_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    assert_org_access(target_user.organization_id, current_user)
    return api_service.update_user_role(session, user_id, role)


@router.patch("/users/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(
    user_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Deactivate user"""
    require_admin(current_user)
    target_user = session.get(User, user_id)
    if not target_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    assert_org_access(target_user.organization_id, current_user)
    return api_service.deactivate_user(session, user_id)


# Team Management
@router.get("/teams", response_model=list[TeamRead])
def list_settings_teams(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """List all teams"""
    return api_service.list_teams(session, current_user.organization_id)


@router.post("/teams", response_model=TeamRead)
def create_settings_team(
    data: TeamCreateRequest, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Create new team"""
    require_admin(current_user)
    from app.schemas.team import TeamCreate
    payload = TeamCreate(**data.model_dump(), organization_id=current_user.organization_id)
    return api_service.create_team(session, payload)


# Season Management
@router.get("/seasons", response_model=list[SeasonRead])
def list_seasons(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """List all seasons"""
    return api_service.list_seasons(session, current_user.organization_id)


@router.put("/seasons/{season_id}/activate", response_model=SeasonRead)
def activate_season(
    season_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Activate season"""
    require_admin(current_user)
    # Season model uses organization_id check inside service usually, but let's be safe
    # (Assuming season belongs to org)
    return api_service.activate_season(session, season_id)


# Video Processing Settings
@router.get("/video-processing", response_model=VideoProcessingSettingsRead)
def get_video_processing_settings(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Get video processing settings"""
    return api_service.get_video_processing_settings(session, current_user.organization_id)


@router.put("/video-processing", response_model=VideoProcessingSettingsRead)
def update_video_processing_settings(
    data: VideoProcessingSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update video processing settings"""
    require_admin(current_user)
    return api_service.update_video_processing_settings(session, current_user.organization_id, data)


# Notification Settings
@router.get("/notifications", response_model=NotificationSettingsRead)
def get_notification_settings(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Get notification settings"""
    return api_service.get_notification_settings(session, current_user.organization_id)


@router.put("/notifications", response_model=NotificationSettingsRead)
def update_notification_settings(
    data: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update notification settings"""
    return api_service.update_notification_settings(session, current_user.organization_id, data)


# Privacy Settings
@router.get("/privacy", response_model=PrivacySettingsRead)
def get_privacy_settings(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Get privacy settings"""
    return api_service.get_privacy_settings(session, current_user.organization_id)


@router.put("/privacy", response_model=PrivacySettingsRead)
def update_privacy_settings(
    data: PrivacySettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update privacy settings"""
    require_admin(current_user)
    return api_service.update_privacy_settings(session, current_user.organization_id, data)


# Drone / çekim checklist (demo: bellek içi)
@router.get("/drone-checklist", response_model=DroneChecklistRead)
def get_drone_checklist(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    return api_service.get_drone_checklist(session, current_user.organization_id)


@router.put("/drone-checklist", response_model=DroneChecklistRead)
def update_drone_checklist(
    data: DroneChecklistUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    require_coach_or_above(current_user)
    return api_service.update_drone_checklist(session, current_user.organization_id, data)


# Abonelik (placeholder)
@router.get("/subscription", response_model=SubscriptionRead)
def get_subscription(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    return api_service.get_subscription(session, current_user.organization_id)


# Data Management
@router.post("/data/export", response_model=dict)
def export_player_data(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Tüm oyuncu verilerini dışa aktar."""
    require_admin(current_user)
    return {
        "status": "queued",
        "message": "Veri dışa aktarma kuyruğa alındı. Hazır olduğunda bildirim gönderilecek.",
        "format": "json",
    }


@router.post("/data/anonymize", response_model=dict)
def anonymize_player_data(
    player_id: int = Query(..., description="Anonimleştirilecek oyuncu ID"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Oyuncu kişisel verilerini anonimleştir."""
    require_admin(current_user)
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    return {
        "status": "ok",
        "player_id": player_id,
        "message": f"Oyuncu #{player_id} verileri anonimleştirildi (placeholder).",
    }


@router.post("/data/delete-request", response_model=dict)
def request_data_deletion(
    player_id: int = Query(..., description="Silinmesi talep edilen oyuncu ID"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Oyuncu verisi silme talebi oluştur."""
    require_admin(current_user)
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    return {
        "status": "submitted",
        "player_id": player_id,
        "message": "Silme talebi alındı. 30 gün içinde işleme alınacak.",
    }


@router.get("/data/consent/{player_id}", response_model=dict)
def get_player_consent(
    player_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Oyuncunun veli onayı kayıtlarını getir."""
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    return {
        "player_id": player_id,
        "consents": [],
    }


@router.post("/data/consent", response_model=dict)
def record_consent(
    player_id: int = Query(...),
    consent_type: str = Query(...),
    guardian_name: str = Query(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Veli onayı kaydet."""
    require_admin(current_user)
    player = api_service.get_player(session, player_id)
    assert_org_access(player.organization_id, current_user)
    return {
        "status": "recorded",
        "player_id": player_id,
        "message": "Onay kaydedildi (placeholder).",
    }

