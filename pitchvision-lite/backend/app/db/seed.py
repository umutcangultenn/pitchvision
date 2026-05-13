"""
Demo / geliştirme ortamı için örnek kayıt üretimi.

Kullanım:
    from sqlmodel import Session
    from app.db.session import engine
    from app.db.seed import seed_demo_data

    with Session(engine) as session:
        seed_demo_data(session)
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import bcrypt
from sqlmodel import Session, select

from app.models import (
    DrillRecommendation,
    Match,
    Organization,
    Player,
    Report,
    Team,
    TacticalAlert,
    User,
    VideoAsset,
)
from app.models.enums import (
    AlertStatus,
    AlertType,
    DrillDifficulty,
    MatchStatus,
    PitchSize,
    ProblemType,
    ReportType,
    Severity,
    UserRole,
    VideoAssetStatus,
    VideoSource,
)
def _hash_password(plain: str) -> str:
    digest = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return digest.decode("utf-8")


def seed_demo_data(session: Session) -> None:
    """Kimlik çakışmalarını önlemek için idempotent: aynı e-posta varsa atlar."""

    demo_email = "admin@demo.pitchvision.local"
    existing = session.exec(select(User).where(User.email == demo_email)).first()
    if existing:
        return

    org = Organization(
        name="Demo Akademi SK",
        city="İstanbul",
        logo_url=None,
        organization_type="academy",
    )
    session.add(org)
    session.commit()
    session.refresh(org)

    team = Team(
        organization_id=org.id,
        name="U14 A",
        age_category="U14",
        game_format="11v11",
        default_formation="4-3-3",
        pitch_length=105.0,
        pitch_width=68.0,
        season="2025-26",
    )
    session.add(team)
    session.commit()
    session.refresh(team)

    user = User(
        email=demo_email,
        full_name="Demo Yönetici",
        hashed_password=_hash_password("demo12345"),
        role=UserRole.ADMIN,
        organization_id=org.id,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    player = Player(
        organization_id=org.id,
        team_id=team.id,
        first_name="Ali",
        last_name="Yılmaz",
        birth_date=date(2011, 5, 3),
        position="CM",
        dominant_foot="right",
        height_cm=162.0,
        weight_kg=52.0,
        technical_score=6.5,
        tactical_score=6.2,
        physical_score=6.8,
        decision_score=6.0,
        development_velocity=0.4,
    )
    session.add(player)
    session.commit()
    session.refresh(player)

    kickoff = datetime(2025, 4, 12, 14, 0, tzinfo=timezone.utc)
    match = Match(
        organization_id=org.id,
        team_id=team.id,
        opponent_name="Rakip Kulüp B",
        match_date=kickoff,
        age_category="U14",
        game_format="11v11",
        pitch_length=105.0,
        pitch_width=68.0,
        first_half_attack_direction="left_to_right",
        score_for=2,
        score_against=1,
        video_source=VideoSource.FILE_UPLOAD,
        status=MatchStatus.COMPLETED,
    )
    session.add(match)
    session.commit()
    session.refresh(match)

    video = VideoAsset(
        match_id=match.id,
        file_name="match_u14_demo.mp4",
        storage_path=f"org/{org.id}/matches/{match.id}/match_u14_demo.mp4",
        duration_seconds=5400.0,
        width=1920,
        height=1080,
        fps=25.0,
        status=VideoAssetStatus.READY,
    )
    session.add(video)
    session.commit()

    alert = TacticalAlert(
        match_id=match.id,
        team_id=team.id,
        player_id=player.id,
        alert_type=AlertType.TRANSITION,
        start_time=1200.0,
        end_time=1245.0,
        confidence=0.82,
        severity=Severity.HIGH,
        status=AlertStatus.OPEN,
        title="Hızlı geçiş fırsatı",
        description="Orta blokta top kazanımı sonrası kanat boşluğu.",
        related_metric=None,
        suggested_clip_id=None,
    )
    session.add(alert)
    session.commit()

    report = Report(
        match_id=match.id,
        player_id=None,
        report_type=ReportType.MATCH_SUMMARY,
        title=f"{match.opponent_name} maçı özeti",
        summary="Özet: baskı ve geçiş oyununda gelişim alanları.",
        html_path=None,
        pdf_path=None,
    )
    session.add(report)

    drill = DrillRecommendation(
        alert_type=AlertType.TRANSITION,
        title="4v4+2 geçiş presi",
        problem_type=ProblemType.TACTICAL,
        age_category="U14",
        duration_minutes=20,
        player_count=10,
        pitch_size=PitchSize.SMALL_SIDED,
        difficulty=DrillDifficulty.MEDIUM,
        description="Orta bölgede top kazanımından sonra 3 pas içinde şut bölgesine giriş.",
        coaching_points_json=[
            {"tr": "Dar alanda ilk dokunuş kalitesi"},
            {"tr": "Kontra pressing tetikleyicisi"},
        ],
    )
    session.add(drill)
    session.commit()
