from collections import Counter
from datetime import datetime, timezone
from secrets import token_hex
from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.security import create_mock_token, hash_password, verify_password
from app.models import (
    Clip,
    DrillRecommendation,
    FieldCalibration,
    Match,
    Organization,
    Player,
    PlayerMatchPerformance,
    Report,
    ScoutNote,
    TacticalAlert,
    TacticalMetric,
    Team,
    TrackPoint,
    User,
    VideoAsset,
)
from app.models.enums import AlertStatus, MatchStatus, MetricType, ReportType, UserRole, VideoAssetStatus
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.drill import DrillRecommendationCreate, DrillRecommendationUpdate
from app.schemas.match import MatchCreate, MatchUpdate
from app.schemas.organization import OrganizationUpdate
from app.schemas.performance import ScoutNoteCreate
from app.schemas.player import PlayerCreate, PlayerUpdate
from app.schemas.report import ReportCreate
from app.schemas.saas import DemoRequestCreate, DemoRequestResponse
from app.schemas.tactical import ClipCreate, TacticalAlertUpdate
from app.schemas.settings import (
    DroneChecklistRead,
    DroneChecklistUpdate,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
    OrganizationSettingsRead,
    OrganizationSettingsUpdate,
    PrivacySettingsRead,
    PrivacySettingsUpdate,
    SeasonRead,
    SubscriptionRead,
    TeamCreateRequest,
    TeamRead as SettingsTeamRead,
    UserInviteRequest,
    UserRead as SettingsUserRead,
    VideoProcessingSettingsRead,
    VideoProcessingSettingsUpdate,
)
from app.schemas.team import TeamCreate, TeamUpdate
from app.schemas.track_point import TrackPointCreate
from app.schemas.video import FieldCalibrationCreate, VideoAssetCreate

T = TypeVar("T")


def _not_found(name: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} bulunamadı.")


def _patch(instance: Any, payload: Any) -> Any:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(instance, key, value)
    return instance


def register(session: Session, payload: RegisterRequest) -> TokenResponse:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı.")

    user = User(
        email=str(payload.email),
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        organization_id=payload.organization_id,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_mock_token(user.id)
    return TokenResponse(access_token=token, user=user)


def login(session: Session, payload: LoginRequest) -> TokenResponse:
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-posta veya parola hatalı.")
    return TokenResponse(access_token=create_mock_token(user.id), user=user)


def list_teams(session: Session, organization_id: int) -> list[Team]:
    return list(session.exec(select(Team).where(Team.organization_id == organization_id)))


def get_team(session: Session, team_id: int) -> Team:
    team = session.get(Team, team_id)
    if not team:
        raise _not_found("Takım")
    return team


def create_team(session: Session, payload: TeamCreate) -> Team:
    team = Team(**payload.model_dump())
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


def update_team(session: Session, team_id: int, payload: TeamUpdate) -> Team:
    team = get_team(session, team_id)
    _patch(team, payload)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


def list_players(session: Session, organization_id: int) -> list[Player]:
    return list(session.exec(select(Player).where(Player.organization_id == organization_id)))


def get_player(session: Session, player_id: int) -> Player:
    player = session.get(Player, player_id)
    if not player:
        raise _not_found("Oyuncu")
    return player


def create_player(session: Session, payload: PlayerCreate) -> Player:
    player = Player(**payload.model_dump())
    session.add(player)
    session.commit()
    session.refresh(player)
    return player


def update_player(session: Session, player_id: int, payload: PlayerUpdate) -> Player:
    player = get_player(session, player_id)
    _patch(player, payload)
    session.add(player)
    session.commit()
    session.refresh(player)
    return player


def list_matches(session: Session, organization_id: int) -> list[Match]:
    return list(session.exec(select(Match).where(Match.organization_id == organization_id)))


def get_match(session: Session, match_id: int) -> Match:
    item = session.get(Match, match_id)
    if not item:
        raise _not_found("Maç")
    return item


def create_match(session: Session, payload: MatchCreate) -> Match:
    item = Match(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def update_match(session: Session, match_id: int, payload: MatchUpdate) -> Match:
    item = get_match(session, match_id)
    _patch(item, payload)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_match(session: Session, match_id: int) -> None:
    item = get_match(session, match_id)
    session.delete(item)
    session.commit()


def upload_video(session: Session, payload: VideoAssetCreate) -> VideoAsset:
    item = VideoAsset(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_match_video(session: Session, match_id: int) -> VideoAsset | None:
    return session.exec(select(VideoAsset).where(VideoAsset.match_id == match_id)).first()


def set_video_processing(session: Session, match_id: int) -> VideoAsset:
    item = get_match_video(session, match_id)
    if not item:
        raise _not_found("Video")
    item.status = VideoAssetStatus.PROCESSING
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def create_calibration(session: Session, payload: FieldCalibrationCreate) -> FieldCalibration:
    item = FieldCalibration(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_calibration(session: Session, match_id: int) -> FieldCalibration | None:
    return session.exec(select(FieldCalibration).where(FieldCalibration.match_id == match_id)).first()


def list_metrics(session: Session, match_id: int) -> list[TacticalMetric]:
    return list(session.exec(select(TacticalMetric).where(TacticalMetric.match_id == match_id)))


def recalculate_metrics(session: Session, match_id: int) -> TacticalMetric:
    match = get_match(session, match_id)
    team_id = match.team_id
    metric = TacticalMetric(
        match_id=match_id,
        team_id=team_id,
        event_timestamp=datetime.now(timezone.utc),
        metric_type=MetricType.CUSTOM,
        value=1.0,
        unit="score",
        metadata_json={"source": "recalculate"},
    )
    session.add(metric)
    session.commit()
    session.refresh(metric)
    return metric


def list_alerts(session: Session, match_id: int) -> list[TacticalAlert]:
    return list(session.exec(select(TacticalAlert).where(TacticalAlert.match_id == match_id)))


def get_alert(session: Session, alert_id: int) -> TacticalAlert:
    item = session.get(TacticalAlert, alert_id)
    if not item:
        raise _not_found("Alert")
    return item


def update_alert(session: Session, alert_id: int, payload: TacticalAlertUpdate) -> TacticalAlert:
    item = get_alert(session, alert_id)
    _patch(item, payload)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def set_alert_status(session: Session, alert_id: int, status_value: AlertStatus) -> TacticalAlert:
    item = get_alert(session, alert_id)
    item.status = status_value
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def list_clips_by_match(session: Session, match_id: int) -> list[Clip]:
    return list(session.exec(select(Clip).where(Clip.match_id == match_id)))


def get_clip(session: Session, clip_id: int) -> Clip:
    item = session.get(Clip, clip_id)
    if not item:
        raise _not_found("Klip")
    return item


def create_clip(session: Session, payload: ClipCreate) -> Clip:
    item = Clip(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def list_reports(session: Session) -> list[Report]:
    return list(session.exec(select(Report).order_by(Report.created_at.desc())))


def get_report(session: Session, report_id: int) -> Report:
    item = session.get(Report, report_id)
    if not item:
        raise _not_found("Rapor")
    return item


def create_report(session: Session, payload: ReportCreate) -> Report:
    item = Report(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def export_report_pdf(session: Session, report_id: int) -> Report:
    item = get_report(session, report_id)
    if not item.pdf_path:
        item.pdf_path = f"reports/{report_id}.pdf"
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def list_scouting_players(session: Session) -> list[Player]:
    return list(session.exec(select(Player).order_by(Player.development_velocity.desc())))


def hidden_gems(session: Session) -> list[Player]:
    items = session.exec(select(Player).where(Player.development_velocity > 0.5)).all()
    return list(items)


def create_scout_note(session: Session, payload: ScoutNoteCreate) -> ScoutNote:
    item = ScoutNote(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def list_player_scout_notes(session: Session, player_id: int) -> list[ScoutNote]:
    return list(session.exec(select(ScoutNote).where(ScoutNote.player_id == player_id)))


def list_drills(session: Session) -> list[DrillRecommendation]:
    return list(session.exec(select(DrillRecommendation).order_by(DrillRecommendation.id)))


def list_match_drills(session: Session, match_id: int) -> list[DrillRecommendation]:
    alerts = list_alerts(session, match_id)
    alert_types = {a.alert_type for a in alerts}
    if not alert_types:
        return list_drills(session)
    return list(
        session.exec(select(DrillRecommendation).where(DrillRecommendation.alert_type.in_(alert_types)))
    )


def get_org(session: Session, organization_id: int) -> Organization:
    item = session.get(Organization, organization_id)
    if not item:
        raise _not_found("Organizasyon")
    return item


def update_org(session: Session, organization_id: int, payload: OrganizationUpdate) -> Organization:
    org = get_org(session, organization_id)
    _patch(org, payload)
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


def player_passport(session: Session, player_id: int) -> dict[str, Any]:
    """Kapsamlı oyuncu pasaportu verileri topla"""
    player = get_player(session, player_id)
    performances = list(session.exec(select(PlayerMatchPerformance).where(PlayerMatchPerformance.player_id == player_id)))
    team = session.exec(select(Team).where(Team.id == player.team_id)).first() if player.team_id else None
    
    # Maç istatistikleri
    matches_played = len(performances)
    avg_max_speed = sum(p.max_speed or 0 for p in performances) / matches_played if matches_played else 0
    avg_speed = sum(p.average_speed or 0 for p in performances) / matches_played if matches_played else 0
    total_positive = sum(p.positive_actions or 0 for p in performances)
    total_alerts = sum(p.alerts_involved or 0 for p in performances)
    
    # 8 haftalık trend (simülasyon)
    trend_data = []
    base_scores = {
        "technical": player.technical_score or 5.0,
        "tactical": player.tactical_score or 5.0,
        "physical": player.physical_score or 5.0,
        "decision": player.decision_score or 5.0,
    }
    
    for week in range(1, 9):
        variance = (week - 4.5) * 0.05  # trend simülasyonu
        trend_data.append({
            "x": f"H{week}",
            "technical": max(1, min(10, base_scores["technical"] + variance)),
            "tactical": max(1, min(10, base_scores["tactical"] + variance * 0.8)),
            "physical": max(1, min(10, base_scores["physical"] + variance * 0.6)),
            "decision": max(1, min(10, base_scores["decision"] + variance * 0.9)),
        })
    
    # Taktiksel profil (pozisyona göre)
    position = player.position.upper()
    tactical_profile = {
        "group": "Genel",
        "metrics": [
            {"label": "Teknik", "value": player.technical_score or 5},
            {"label": "Taktik", "value": player.tactical_score or 5},
            {"label": "Fiziksel", "value": player.physical_score or 5},
            {"label": "Karar", "value": player.decision_score or 5},
        ]
    }
    
    if position in ["CB", "LB", "RB", "SW"]:
        tactical_profile = {
            "group": "Stoper / Bek",
            "metrics": [
                {"label": "Hat Uyumu", "value": (player.tactical_score or 5) * 0.95},
                {"label": "Savunma Arkası Kontrol", "value": (player.tactical_score or 5) * 0.90},
                {"label": "Topla Çıkış", "value": (player.technical_score or 5) * 0.85},
                {"label": "Baskı Altında Pas", "value": (player.decision_score or 5) * 0.88},
            ]
        }
    elif position in ["CM", "CDM", "CAM", "DM"]:
        tactical_profile = {
            "group": "Merkez Orta Saha",
            "metrics": [
                {"label": "Pas Bağlantısı", "value": (player.technical_score or 5) * 0.92},
                {"label": "Destek Açısı", "value": (player.tactical_score or 5) * 0.88},
                {"label": "Geçiş Savunması", "value": (player.tactical_score or 5) * 0.85},
                {"label": "Top Alma Konumu", "value": (player.decision_score or 5) * 0.90},
            ]
        }
    elif position in ["LW", "RW", "LM", "RM", "WF"]:
        tactical_profile = {
            "group": "Kanat",
            "metrics": [
                {"label": "Derin Koşu", "value": (player.physical_score or 5) * 0.90},
                {"label": "Genişlik Koruma", "value": (player.tactical_score or 5) * 0.85},
                {"label": "1v1 Katkı", "value": (player.technical_score or 5) * 0.88},
                {"label": "Geri Dönüş Savunması", "value": (player.physical_score or 5) * 0.82},
            ]
        }
    elif position in ["ST", "CF", "SS"]:
        tactical_profile = {
            "group": "Forvet",
            "metrics": [
                {"label": "Bitiricilik", "value": (player.technical_score or 5) * 0.92},
                {"label": "Hareket Kalitesi", "value": (player.physical_score or 5) * 0.88},
                {"label": "Bağlantı Oyunu", "value": (player.decision_score or 5) * 0.85},
                {"label": "Pres Katkısı", "value": (player.tactical_score or 5) * 0.80},
            ]
        }
    
    return {
        "player_id": player.id,
        "first_name": player.first_name,
        "last_name": player.last_name,
        "birth_date": player.birth_date.isoformat(),
        "position": player.position,
        "dominant_foot": player.dominant_foot,
        "height_cm": player.height_cm,
        "weight_kg": player.weight_kg,
        "photo_url": player.photo_url,
        "team_name": team.name if team else None,
        "technical_score": player.technical_score,
        "tactical_score": player.tactical_score,
        "physical_score": player.physical_score,
        "decision_score": player.decision_score,
        "development_velocity": player.development_velocity,
        "matches_played": matches_played,
        "average_max_speed": round(avg_max_speed, 1),
        "average_speed": round(avg_speed, 1),
        "total_positive_actions": total_positive,
        "total_alerts_involved": total_alerts,
        "trend_data": trend_data,
        "tactical_profile": tactical_profile,
    }


def player_performances(session: Session, player_id: int) -> list[PlayerMatchPerformance]:
    return list(session.exec(select(PlayerMatchPerformance).where(PlayerMatchPerformance.player_id == player_id)))


def player_clips(session: Session, player_id: int) -> list[Clip]:
    return list(session.exec(select(Clip).where(Clip.player_id == player_id)))


def match_summary(session: Session, match_id: int) -> dict[str, Any]:
    match = get_match(session, match_id)
    alerts_count = len(list_alerts(session, match_id))
    clips_count = len(list_clips_by_match(session, match_id))
    return {
        "match_id": match.id,
        "opponent_name": match.opponent_name,
        "score": f"{match.score_for}-{match.score_against}",
        "status": match.status,
        "alerts_count": alerts_count,
        "clips_count": clips_count,
    }


def match_report(session: Session, match_id: int) -> Report | None:
    return session.exec(select(Report).where(Report.match_id == match_id)).first()


def run_calibration_test(session: Session, payload: TrackPointCreate) -> TrackPoint:
    item = TrackPoint(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def start_match_processing(session: Session, match_id: int) -> Match:
    match = get_match(session, match_id)
    match.status = MatchStatus.PROCESSING
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def ensure_demo_seed(session: Session) -> None:
    # Seed önceki adımda mevcut; bu kanca endpoint öncesi çağrılar için hazır.
    _ = session


def force_create_drill(session: Session, payload: DrillRecommendationCreate) -> DrillRecommendation:
    item = DrillRecommendation(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def force_update_drill(session: Session, drill_id: int, payload: DrillRecommendationUpdate) -> DrillRecommendation:
    item = session.get(DrillRecommendation, drill_id)
    if not item:
        raise _not_found("Drill")
    _patch(item, payload)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


# --- PitchVision Lite: Ayarlar (DB + bellek içi ek alanlar) ---

_LITE_SETTINGS: dict[str, Any] = {
    "org_contact": {},
    "video": {
        "default_pitch_size": "105x68m",
        "default_game_format": "11v11",
        "detection_confidence_threshold": 0.72,
        "alert_threshold_value": 0.55,
        "default_clip_duration": 12,
    },
    "notifications": {
        "notify_analysis_complete": True,
        "notify_errors": True,
        "notify_new_report": True,
        "notify_scout_note": True,
        "notify_player_development": True,
    },
    "privacy": {
        "anonymize_player_data": False,
        "gdpr_enabled": True,
        "parental_consent_required": True,
        "u8_u17_data_security_enabled": True,
    },
    "active_season_id": None,
    "season_name_to_id": {},
    "season_id_to_name": {},
    "next_season_id": 1,
    "drone": {
        "flight_permission_checked": False,
        "pitch_safety_secured": False,
        "parent_player_consents_checked": False,
        "camera_angle_ok": False,
        "pitch_lines_visible": False,
        "wind_weather_ok": False,
    },
}


def _first_organization(session: Session) -> Organization:
    org = session.exec(select(Organization)).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organizasyon bulunamadı.")
    return org


def _org_contact(org_id: int) -> dict[str, Any]:
    return _LITE_SETTINGS["org_contact"].setdefault(
        org_id,
        {"contact_email": None, "contact_phone": None, "website": None},
    )


def get_organization_settings(session: Session) -> OrganizationSettingsRead:
    org = _first_organization(session)
    extra = _org_contact(org.id)
    return OrganizationSettingsRead(
        id=org.id,
        name=org.name,
        city=org.city,
        logo_url=org.logo_url,
        organization_type=org.organization_type,
        contact_email=extra.get("contact_email"),
        contact_phone=extra.get("contact_phone"),
        website=extra.get("website"),
    )


def update_organization_settings(
    session: Session, data: OrganizationSettingsUpdate
) -> OrganizationSettingsRead:
    org = _first_organization(session)
    org.name = data.name
    org.city = data.city
    org.logo_url = data.logo_url
    org.organization_type = data.organization_type
    session.add(org)
    session.commit()
    session.refresh(org)
    extra = _org_contact(org.id)
    extra["contact_email"] = data.contact_email
    extra["contact_phone"] = data.contact_phone
    extra["website"] = data.website
    return get_organization_settings(session)


def list_users(session: Session) -> list[SettingsUserRead]:
    org = _first_organization(session)
    users = list(session.exec(select(User).where(User.organization_id == org.id)))
    out: list[SettingsUserRead] = []
    for u in users:
        out.append(
            SettingsUserRead(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=u.role.value if isinstance(u.role, UserRole) else str(u.role),
                is_active=u.is_active,
                created_at=u.created_at.isoformat() if u.created_at else None,
            )
        )
    return out


def invite_user(session: Session, data: UserInviteRequest) -> dict[str, str]:
    _ = session, data
    return {
        "status": "ok",
        "message": f"Davet e-postası kuyruğa alındı: {data.email}",
    }


def update_user_role(session: Session, user_id: int, role: str) -> SettingsUserRead:
    try:
        role_enum = UserRole(role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Geçersiz rol.") from exc
    user = session.get(User, user_id)
    if not user:
        raise _not_found("Kullanıcı")
    user.role = role_enum
    session.add(user)
    session.commit()
    session.refresh(user)
    return SettingsUserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


def deactivate_user(session: Session, user_id: int) -> SettingsUserRead:
    user = session.get(User, user_id)
    if not user:
        raise _not_found("Kullanıcı")
    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)
    return SettingsUserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


def settings_list_teams(session: Session) -> list[SettingsTeamRead]:
    org = _first_organization(session)
    teams = list(session.exec(select(Team).where(Team.organization_id == org.id)))
    return [
        SettingsTeamRead(
            id=t.id,
            name=t.name,
            age_category=t.age_category,
            game_format=t.game_format,
            default_formation=t.default_formation,
            pitch_length=t.pitch_length,
            pitch_width=t.pitch_width,
            season=t.season,
            is_active=True,
        )
        for t in teams
    ]


def settings_create_team(session: Session, data: TeamCreateRequest) -> SettingsTeamRead:
    org = _first_organization(session)
    org_id = data.organization_id if data.organization_id is not None else org.id
    season = data.season or "2025-26"
    payload = TeamCreate(
        organization_id=org_id,
        name=data.name,
        age_category=data.age_category,
        game_format=data.game_format,
        default_formation=data.default_formation,
        pitch_length=data.pitch_length,
        pitch_width=data.pitch_width,
        season=season,
    )
    team = create_team(session, payload)
    return SettingsTeamRead(
        id=team.id,
        name=team.name,
        age_category=team.age_category,
        game_format=team.game_format,
        default_formation=team.default_formation,
        pitch_length=team.pitch_length,
        pitch_width=team.pitch_width,
        season=team.season,
        is_active=True,
    )


def _register_season_names(names: list[str]) -> None:
    for name in names:
        if name not in _LITE_SETTINGS["season_name_to_id"]:
            sid = _LITE_SETTINGS["next_season_id"]
            _LITE_SETTINGS["next_season_id"] += 1
            _LITE_SETTINGS["season_name_to_id"][name] = sid
            _LITE_SETTINGS["season_id_to_name"][sid] = name


def list_seasons(session: Session) -> list[SeasonRead]:
    org = _first_organization(session)
    teams = list(session.exec(select(Team).where(Team.organization_id == org.id)))
    unique = sorted({t.season for t in teams}) if teams else ["2025-26"]
    _register_season_names(unique)
    counts = Counter(t.season for t in teams)
    active_id = _LITE_SETTINGS["active_season_id"]
    out: list[SeasonRead] = []
    for name in unique:
        sid = _LITE_SETTINGS["season_name_to_id"][name]
        out.append(
            SeasonRead(
                id=sid,
                name=name,
                start_date="2025-07-01",
                end_date="2026-06-15",
                is_active=(active_id == sid),
                teams_count=counts.get(name, 0),
            )
        )
    if out and active_id is None:
        out[0] = out[0].model_copy(update={"is_active": True})
    return out


def activate_season(session: Session, season_id: int) -> SeasonRead:
    name = _LITE_SETTINGS["season_id_to_name"].get(season_id)
    if not name:
        list_seasons(session)
        name = _LITE_SETTINGS["season_id_to_name"].get(season_id)
    if not name:
        raise _not_found("Sezon")
    _LITE_SETTINGS["active_season_id"] = season_id
    org = _first_organization(session)
    teams = list(session.exec(select(Team).where(Team.organization_id == org.id)))
    return SeasonRead(
        id=season_id,
        name=name,
        start_date="2025-07-01",
        end_date="2026-06-15",
        is_active=True,
        teams_count=len([t for t in teams if t.season == name]),
    )


def get_video_processing_settings(session: Session) -> VideoProcessingSettingsRead:
    _ = session
    return VideoProcessingSettingsRead(**_LITE_SETTINGS["video"])


def update_video_processing_settings(
    session: Session, data: VideoProcessingSettingsUpdate
) -> VideoProcessingSettingsRead:
    _ = session
    _LITE_SETTINGS["video"].update(data.model_dump())
    return VideoProcessingSettingsRead(**_LITE_SETTINGS["video"])


def get_notification_settings(session: Session) -> NotificationSettingsRead:
    _ = session
    return NotificationSettingsRead(**_LITE_SETTINGS["notifications"])


def update_notification_settings(
    session: Session, data: NotificationSettingsUpdate
) -> NotificationSettingsRead:
    _ = session
    _LITE_SETTINGS["notifications"].update(data.model_dump())
    return NotificationSettingsRead(**_LITE_SETTINGS["notifications"])


def get_privacy_settings(session: Session) -> PrivacySettingsRead:
    _ = session
    return PrivacySettingsRead(**_LITE_SETTINGS["privacy"])


def update_privacy_settings(session: Session, data: PrivacySettingsUpdate) -> PrivacySettingsRead:
    _ = session
    _LITE_SETTINGS["privacy"].update(data.model_dump())
    return PrivacySettingsRead(**_LITE_SETTINGS["privacy"])


def get_drone_checklist(session: Session) -> DroneChecklistRead:
    _ = session
    return DroneChecklistRead(**_LITE_SETTINGS["drone"])


def update_drone_checklist(session: Session, data: DroneChecklistUpdate) -> DroneChecklistRead:
    _ = session
    _LITE_SETTINGS["drone"].update(data.model_dump())
    return DroneChecklistRead(**_LITE_SETTINGS["drone"])


def get_subscription(session: Session) -> SubscriptionRead:
    org = _first_organization(session)
    users = list(session.exec(select(User).where(User.organization_id == org.id)))
    n = len(users)
    return SubscriptionRead(
        plan_name="Academy",
        billing_cycle="Yıllık",
        next_renewal="2027-01-15",
        seats_used=n,
        seats_limit=max(10, n + 2),
        status="active",
    )


def submit_demo_request(payload: DemoRequestCreate) -> DemoRequestResponse:
    """Demo talebini kaydet (MVP: yanıt üretir; kalıcı kuyruk yok)."""
    _ = payload
    return DemoRequestResponse(status="received", reference=f"DEMO-{token_hex(4).upper()}")
