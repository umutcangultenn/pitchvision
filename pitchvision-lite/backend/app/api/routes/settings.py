from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.db.session import get_session
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

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=AppSettingsRead)
def get_settings(_: Session = Depends(get_session)) -> AppSettingsRead:
    api_service.ensure_demo_seed(_)
    return AppSettingsRead(app_name="PitchVision Lite API", debug=False)


# Organization Settings
@router.get("/organization", response_model=OrganizationSettingsRead)
def get_organization_settings(session: Session = Depends(get_session)):
    """Get organization settings"""
    return api_service.get_organization_settings(session)


@router.put("/organization", response_model=OrganizationSettingsRead)
def update_organization_settings(
    data: OrganizationSettingsUpdate,
    session: Session = Depends(get_session),
):
    """Update organization settings"""
    return api_service.update_organization_settings(session, data)


# User Management
@router.get("/users", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session)):
    """List all users in organization"""
    return api_service.list_users(session)


@router.post("/users/invite", response_model=dict)
def invite_user(data: UserInviteRequest, session: Session = Depends(get_session)):
    """Invite user to organization"""
    return api_service.invite_user(session, data)


@router.put("/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    role: str = Query(..., description="Yeni rol"),
    session: Session = Depends(get_session),
):
    """Update user role"""
    return api_service.update_user_role(session, user_id, role)


@router.patch("/users/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(user_id: int, session: Session = Depends(get_session)):
    """Deactivate user"""
    return api_service.deactivate_user(session, user_id)


# Team Management
@router.get("/teams", response_model=list[TeamRead])
def list_settings_teams(session: Session = Depends(get_session)):
    """List all teams"""
    return api_service.settings_list_teams(session)


@router.post("/teams", response_model=TeamRead)
def create_settings_team(data: TeamCreateRequest, session: Session = Depends(get_session)):
    """Create new team"""
    return api_service.settings_create_team(session, data)


# Season Management
@router.get("/seasons", response_model=list[SeasonRead])
def list_seasons(session: Session = Depends(get_session)):
    """List all seasons"""
    return api_service.list_seasons(session)


@router.put("/seasons/{season_id}/activate", response_model=SeasonRead)
def activate_season(season_id: int, session: Session = Depends(get_session)):
    """Activate season"""
    return api_service.activate_season(session, season_id)


# Video Processing Settings
@router.get("/video-processing", response_model=VideoProcessingSettingsRead)
def get_video_processing_settings(session: Session = Depends(get_session)):
    """Get video processing settings"""
    return api_service.get_video_processing_settings(session)


@router.put("/video-processing", response_model=VideoProcessingSettingsRead)
def update_video_processing_settings(
    data: VideoProcessingSettingsUpdate,
    session: Session = Depends(get_session),
):
    """Update video processing settings"""
    return api_service.update_video_processing_settings(session, data)


# Notification Settings
@router.get("/notifications", response_model=NotificationSettingsRead)
def get_notification_settings(session: Session = Depends(get_session)):
    """Get notification settings"""
    return api_service.get_notification_settings(session)


@router.put("/notifications", response_model=NotificationSettingsRead)
def update_notification_settings(
    data: NotificationSettingsUpdate,
    session: Session = Depends(get_session),
):
    """Update notification settings"""
    return api_service.update_notification_settings(session, data)


# Privacy Settings
@router.get("/privacy", response_model=PrivacySettingsRead)
def get_privacy_settings(session: Session = Depends(get_session)):
    """Get privacy settings"""
    return api_service.get_privacy_settings(session)


@router.put("/privacy", response_model=PrivacySettingsRead)
def update_privacy_settings(
    data: PrivacySettingsUpdate,
    session: Session = Depends(get_session),
):
    """Update privacy settings"""
    return api_service.update_privacy_settings(session, data)


# Drone / çekim checklist (demo: bellek içi)
@router.get("/drone-checklist", response_model=DroneChecklistRead)
def get_drone_checklist(session: Session = Depends(get_session)):
    return api_service.get_drone_checklist(session)


@router.put("/drone-checklist", response_model=DroneChecklistRead)
def update_drone_checklist(
    data: DroneChecklistUpdate,
    session: Session = Depends(get_session),
):
    return api_service.update_drone_checklist(session, data)


# Abonelik (placeholder)
@router.get("/subscription", response_model=SubscriptionRead)
def get_subscription(session: Session = Depends(get_session)):
    return api_service.get_subscription(session)


# Data Management
@router.post("/data/export", response_model=dict)
def export_player_data(session: Session = Depends(get_session)):
    """
    Tüm oyuncu verilerini dışa aktar.

    TODO: Gerçek implementasyon:
    - Tüm oyuncu kayıtlarını JSON/CSV olarak hazırla
    - Storage'a yükle ve indirme URL'i döndür
    - AuditLog kaydı oluştur
    - KVKK madde 11 — veri sahibinin erişim hakkı
    """
    return {
        "status": "queued",
        "message": "Veri dışa aktarma kuyruğa alındı. Hazır olduğunda bildirim gönderilecek.",
        "format": "json",
        # TODO: "download_url": "<signed_url>",
        # TODO: "expires_at": "<iso_datetime>",
    }


@router.post("/data/anonymize", response_model=dict)
def anonymize_player_data(
    player_id: int = Query(..., description="Anonimleştirilecek oyuncu ID"),
    session: Session = Depends(get_session),
):
    """
    Oyuncu kişisel verilerini anonimleştir.

    TODO: Gerçek implementasyon:
    - first_name / last_name → rastgele token ile değiştir
    - birth_date → yalnızca yıl bırak
    - photo_url → sil
    - AuditLog kaydı oluştur (action=DATA_ANONYMIZE)
    - İlgili ScoutNote ve PlayerMatchPerformance kayıtlarını güncelle
    """
    player = session.get(__import__("app.models", fromlist=["Player"]).Player, player_id)
    if not player:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı.")

    return {
        "status": "ok",
        "player_id": player_id,
        "message": f"Oyuncu #{player_id} verileri anonimleştirildi (placeholder — gerçek silme yapılmadı).",
        # TODO: Gerçek anonimleştirme burada yapılacak
    }


@router.post("/data/delete-request", response_model=dict)
def request_data_deletion(
    player_id: int = Query(..., description="Silinmesi talep edilen oyuncu ID"),
    session: Session = Depends(get_session),
):
    """
    Oyuncu verisi silme talebi oluştur.

    TODO: Gerçek implementasyon:
    - Silme talebini bir kuyruk/tablo'ya kaydet
    - Yöneticiye bildirim gönder
    - AuditLog kaydı oluştur (action=DATA_DELETE)
    - KVKK madde 7 — silme ve yok etme hakkı
    - 30 gün içinde işleme zorunluluğu
    """
    return {
        "status": "submitted",
        "player_id": player_id,
        "message": "Silme talebi alındı. 30 gün içinde işleme alınacak.",
        "reference": f"DEL-{player_id}-{__import__('time').strftime('%Y%m%d')}",
        # TODO: Gerçek silme iş akışı burada başlatılacak
    }


@router.get("/data/consent/{player_id}", response_model=dict)
def get_player_consent(
    player_id: int,
    session: Session = Depends(get_session),
):
    """
    Oyuncunun veli onayı kayıtlarını getir.

    TODO: ParentalConsent tablosundan gerçek kayıtları döndür.
    """
    return {
        "player_id": player_id,
        "consents": [],  # TODO: ParentalConsent.query(player_id=player_id)
        "message": "Veli onayı kayıtları (placeholder — tablo henüz aktif değil).",
    }


@router.post("/data/consent", response_model=dict)
def record_consent(
    player_id: int = Query(...),
    consent_type: str = Query(..., description="video_recording | data_processing | performance_analysis"),
    guardian_name: str = Query(...),
    session: Session = Depends(get_session),
):
    """
    Veli onayı kaydet.

    TODO: ParentalConsent tablosuna kayıt ekle + AuditLog.
    """
    return {
        "status": "recorded",
        "player_id": player_id,
        "consent_type": consent_type,
        "guardian_name": guardian_name,
        "message": "Onay kaydedildi (placeholder — DB'ye yazılmadı).",
    }
