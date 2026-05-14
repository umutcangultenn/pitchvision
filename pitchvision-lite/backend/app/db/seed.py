"""
Demo / geliştirme ortamı için örnek kayıt üretimi — Anadolu Akademi.

Kullanım:
    python -m app.db.seed          # doğrudan çalıştır
    python scripts/seed_demo.py    # wrapper script
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.core.security import hash_password


# ── helpers ───────────────────────────────────────────────────────────────────

def _hash(plain: str) -> str:
    return hash_password(plain)


def _dt(*args: int) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)  # type: ignore[arg-type]


# ── main entry ────────────────────────────────────────────────────────────────

def seed_demo_data(session: Session) -> None:
    """İdempotent: demo e-posta zaten varsa çıkar."""
    DEMO_EMAIL = "coach@anadolu-akademi.demo"
    if session.exec(select(User).where(User.email == DEMO_EMAIL)).first():
        print("Seed already applied — skipping.")
        return

    # ── Organization ─────────────────────────────────────────────────────────
    org = Organization(
        name="Anadolu Akademi",
        city="İstanbul",
        logo_url=None,
        organization_type="academy",
    )
    session.add(org)
    session.commit(); session.refresh(org)


    # ── Teams ─────────────────────────────────────────────────────────────────
    def _team(name: str, age: str, formation: str) -> Team:
        return Team(
            organization_id=org.id,
            name=name,
            age_category=age,
            game_format="11v11",
            default_formation=formation,
            pitch_length=105.0,
            pitch_width=68.0,
            season="2025/26",
        )

    t_u15 = _team("U15 Kırmızı Takım", "U15", "4-3-3")
    t_u13 = _team("U13 Akademi",        "U13", "4-4-2")
    t_u17 = _team("U17 Gelişim",        "U17", "4-2-3-1")
    t_u11 = _team("U11 Futbol Okulu",   "U11", "4-3-3")
    for t in (t_u15, t_u13, t_u17, t_u11):
        session.add(t)
    session.commit()
    for t in (t_u15, t_u13, t_u17, t_u11):
        session.refresh(t)

    # ── Users ─────────────────────────────────────────────────────────────────
    admin_user = User(
        email="admin@anadolu-akademi.demo",
        full_name="Ahmet Yönetici",
        hashed_password=_hash("demo12345"),
        role=UserRole.ADMIN,
        organization_id=org.id,
        is_active=True,
    )
    coach_user = User(
        email=DEMO_EMAIL,
        full_name="Mehmet Antrenör",
        hashed_password=_hash("demo12345"),
        role=UserRole.COACH,
        organization_id=org.id,
        is_active=True,
    )
    scout_user = User(
        email="scout@anadolu-akademi.demo",
        full_name="Selin Gözlemci",
        hashed_password=_hash("demo12345"),
        role=UserRole.SCOUT,
        organization_id=org.id,
        is_active=True,
    )
    analyst_user = User(
        email="analyst@anadolu-akademi.demo",
        full_name="Caner Analist",
        hashed_password=_hash("demo12345"),
        role=UserRole.ANALYST,
        organization_id=org.id,
        is_active=True,
    )
    for u in (admin_user, coach_user, scout_user, analyst_user):
        session.add(u)
    session.commit()
    for u in (admin_user, coach_user, scout_user, analyst_user):
        session.refresh(u)



    # ── Players ───────────────────────────────────────────────────────────────
    def _player(
        team: Team,
        first: str, last: str,
        birth: date, pos: str, foot: str,
        h: float, w: float,
        tech: float, tact: float, phys: float, dec: float, vel: float,
    ) -> Player:
        return Player(
            organization_id=org.id,
            team_id=team.id,
            first_name=first, last_name=last,
            birth_date=birth, position=pos, dominant_foot=foot,
            height_cm=h, weight_kg=w,
            technical_score=tech, tactical_score=tact,
            physical_score=phys, decision_score=dec,
            development_velocity=vel,
        )

    p_arda  = _player(t_u15, "Arda",  "Yılmaz", date(2011, 3, 14), "CM",  "right", 168, 58, 7.4, 7.1, 6.8, 7.0, 0.52)
    p_emir  = _player(t_u15, "Emir",  "Kaya",   date(2011, 7, 22), "CB",  "right", 176, 68, 6.5, 7.6, 7.2, 7.0, 0.45)
    p_kerem = _player(t_u15, "Kerem", "Demir",  date(2010, 11, 5), "RW",  "right", 170, 60, 7.8, 7.0, 7.1, 7.3, 0.61)
    p_mert  = _player(t_u17, "Mert",  "Şahin",  date(2009, 2, 18), "ST",  "right", 180, 72, 7.2, 6.9, 7.5, 7.1, 0.58)
    p_efe   = _player(t_u13, "Efe",   "Arslan", date(2013, 5, 30), "LB",  "left",  162, 52, 6.2, 6.8, 6.5, 6.4, 0.38)
    p_can   = _player(t_u15, "Can",   "Öztürk", date(2011, 9, 11), "GK",  "right", 178, 70, 6.0, 7.2, 7.0, 7.4, 0.44)

    for p in (p_arda, p_emir, p_kerem, p_mert, p_efe, p_can):
        session.add(p)
    session.commit()
    for p in (p_arda, p_emir, p_kerem, p_mert, p_efe, p_can):
        session.refresh(p)


    # ── Matches ───────────────────────────────────────────────────────────────
    def _match(
        team: Team, opponent: str, dt: datetime,
        sf: int, sa: int, status: MatchStatus,
    ) -> Match:
        return Match(
            organization_id=org.id,
            team_id=team.id,
            opponent_name=opponent,
            match_date=dt,
            age_category=team.age_category,
            game_format=team.game_format,
            pitch_length=team.pitch_length,
            pitch_width=team.pitch_width,
            first_half_attack_direction="left_to_right",
            score_for=sf, score_against=sa,
            video_source=VideoSource.FILE_UPLOAD,
            status=status,
        )

    m_u15  = _match(t_u15, "Mavi Spor",     _dt(2026, 4, 12, 13, 0), 3, 1, MatchStatus.COMPLETED)
    m_u13  = _match(t_u13, "Kartal Akademi", _dt(2026, 4, 19, 11, 0), 2, 2, MatchStatus.COMPLETED)
    m_u17  = _match(t_u17, "Anadolu FK",     _dt(2026, 4, 26, 14, 0), 1, 0, MatchStatus.PROCESSING)
    m_u11  = _match(t_u11, "Kuzey Gençlik",  _dt(2026, 5,  3, 10, 0), 4, 2, MatchStatus.COMPLETED)

    for m in (m_u15, m_u13, m_u17, m_u11):
        session.add(m)
    session.commit()
    for m in (m_u15, m_u13, m_u17, m_u11):
        session.refresh(m)

    # ── VideoAssets ───────────────────────────────────────────────────────────
    def _video(match: Match, fname: str, status: VideoAssetStatus, dur: float | None = 5400.0) -> VideoAsset:
        return VideoAsset(
            match_id=match.id,
            file_name=fname,
            storage_path=f"org/{org.id}/matches/{match.id}/{fname}",
            duration_seconds=dur,
            width=1920, height=1080, fps=25.0,
            status=status,
        )

    session.add(_video(m_u15, "u15_mavi_spor.mp4",      VideoAssetStatus.READY))
    session.add(_video(m_u13, "u13_kartal_akademi.mp4",  VideoAssetStatus.READY))
    session.add(_video(m_u17, "u17_anadolu_fk.mp4",      VideoAssetStatus.PROCESSING, None))
    session.add(_video(m_u11, "u11_kuzey_genclik.mp4",   VideoAssetStatus.READY, 3600.0))
    session.commit()


    # ── TacticalAlerts ────────────────────────────────────────────────────────
    alerts_data = [
        # U15 vs Mavi Spor
        (m_u15, t_u15, p_emir,  AlertType.DEFENSIVE_LINE_BREAK,   450,  510, 0.82, Severity.HIGH,     AlertStatus.OPEN,      "Savunma hattı bozulması",        "Savunma hattı senkronizasyonu bozuldu, rakip derin koşuya alan açıldı."),
        (m_u15, t_u15, p_arda,  AlertType.BLOCK_GAP_WIDE,         820,  880, 0.76, Severity.HIGH,     AlertStatus.IN_REVIEW, "Bloklar arası kopukluk",         "Savunma ve orta saha bloğu arasında 28 m boşluk oluştu."),
        (m_u15, t_u15, p_arda,  AlertType.POOR_TRANSITION_DEFENSE,1200, 1260, 0.79, Severity.CRITICAL, AlertStatus.OPEN,     "Geçiş savunması zayıf",          "Top kaybı sonrası 5 saniyede geri dönüş sağlanamadı."),
        (m_u15, t_u15, p_kerem, AlertType.DEPTH_RUN_OPPORTUNITY,  1540, 1600, 0.87, Severity.MEDIUM,   AlertStatus.RESOLVED, "Derin koşu fırsatı",             "Savunma hattı arkasında derin koşu için uygun zamanlama yakalandı."),
        (m_u15, t_u15, p_arda,  AlertType.LACK_OF_SUPPORT_RUN,    2100, 2160, 0.71, Severity.MEDIUM,   AlertStatus.OPEN,     "Destek koşusu eksikliği",        "Top taşıyıcı için pas opsiyonu oluşturulamadı."),
        (m_u15, t_u15, p_emir,  AlertType.COMPACTNESS_LOST,       2800, 2870, 0.68, Severity.HIGH,     AlertStatus.OPEN,     "Kompaktlık problemi",            "Takım kompaktlığı 28 m'ye çıktı, blok mesafesi aşıldı."),
        # U13 vs Kartal Akademi
        (m_u13, t_u13, p_efe,   AlertType.DEFENSIVE_LINE_BREAK,   310,  370, 0.74, Severity.MEDIUM,   AlertStatus.OPEN,     "Savunma hattı bozulması",        "Sol bek pozisyonu hat dışına çıktı."),
        (m_u13, t_u13, p_efe,   AlertType.TRANSITION,             950, 1010, 0.65, Severity.LOW,      AlertStatus.RESOLVED, "Geçiş organizasyonu",            "Top kazanımı sonrası hızlı geçiş fırsatı değerlendirilemedi."),
    ]

    alert_objs: list[TacticalAlert] = []
    for (match, team, player, atype, st, et, conf, sev, stat, title, desc) in alerts_data:
        a = TacticalAlert(
            match_id=match.id, team_id=team.id, player_id=player.id,
            alert_type=atype, start_time=float(st), end_time=float(et),
            confidence=conf, severity=sev, status=stat,
            title=title, description=desc,
        )
        session.add(a)
        alert_objs.append(a)
    session.commit()
    for a in alert_objs:
        session.refresh(a)


    # ── Clips ─────────────────────────────────────────────────────────────────
    clips_data = [
        (m_u15, alert_objs[2], p_arda,  "Geçiş savunması açığı",       "Top kaybı sonrası 5 sn reaksiyon eksikliği.",  1200, 1260, "transition"),
        (m_u15, alert_objs[3], p_kerem, "Derin koşu — sağ kanat",       "Savunma arkasına zamanlanmış koşu.",           1540, 1600, "depth_run"),
        (m_u15, alert_objs[0], p_emir,  "Savunma hattı kayması",        "Hat senkronizasyonu bozulması anı.",            450,  510, "defensive_line"),
        (m_u13, alert_objs[6], p_efe,   "Sol bek hat dışı",             "Savunma hattı bozulması — sol taraf.",          310,  370, "defensive_line"),
    ]

    for (match, alert, player, title, desc, st, et, tag) in clips_data:
        session.add(Clip(
            match_id=match.id, alert_id=alert.id, player_id=player.id,
            title=title, description=desc,
            start_time=float(st), end_time=float(et), tag=tag,
            storage_path=f"org/{org.id}/clips/{match.id}_{st}.mp4",
        ))
    session.commit()

    # ── TacticalMetrics ───────────────────────────────────────────────────────
    metrics_data = [
        # U15 match — key shape metrics
        (m_u15, t_u15, _dt(2026, 4, 12, 13, 12), MetricType.FIELD_TILT,          0.63,  "",       {"hint": "kanat baskınlığı"}),
        (m_u15, t_u15, _dt(2026, 4, 12, 13, 20), MetricType.PPDA,                8.4,   "",       {"phase": "pressing"}),
        (m_u15, t_u15, _dt(2026, 4, 12, 13, 30), MetricType.PROGRESSIVE_PASSES,  11,    "passes", {"phase": "transition"}),
        (m_u15, t_u15, _dt(2026, 4, 12, 13, 45), MetricType.XG,                  1.82,  "",       {}),
    ]

    for (match, team, ts, mtype, val, unit, meta) in metrics_data:
        session.add(TacticalMetric(
            match_id=match.id, team_id=team.id,
            event_timestamp=ts, metric_type=mtype,
            value=val, unit=unit, metadata_json=meta,
        ))
    session.commit()


    # ── PlayerMatchPerformances ───────────────────────────────────────────────
    perfs_data = [
        # U15 vs Mavi Spor
        (p_arda,  m_u15, 82, 0.48, 0.55, 31.2, 22.1, 7.1, 7.4, 6.8, 7.0, 2, 21, "Orta blok geçişlerinde ilk hamle kalitesi iyileştirilmeli."),
        (p_emir,  m_u15, 90, 0.22, 0.50, 28.4, 20.3, 7.6, 6.5, 7.2, 7.0, 2, 14, "Savunma hattı uyumu iyi, derin koşu kapama geliştirilmeli."),
        (p_kerem, m_u15, 78, 0.72, 0.44, 34.8, 23.5, 7.0, 7.8, 7.1, 7.3, 1, 26, "Kanat çizgisi ile iç koridor arasındaki seçim daha erken tetiklenmeli."),
        (p_can,   m_u15, 90, 0.10, 0.50, 22.1, 14.2, 7.2, 6.0, 7.0, 7.4, 0, 8,  "Uzun pas isabeti yüksek, çıkış kararları gelişiyor."),
        # U13 vs Kartal Akademi
        (p_efe,   m_u13, 75, 0.18, 0.52, 27.6, 19.8, 6.8, 6.2, 6.5, 6.4, 1, 11, "Hat disiplini gelişiyor, pozisyon alma hızı artırılmalı."),
        # U17 vs Anadolu FK
        (p_mert,  m_u17, 85, 0.68, 0.42, 33.5, 22.8, 6.9, 7.2, 7.5, 7.1, 0, 19, "Bitiricilik ve hareket kalitesi maç boyunca tutarlıydı."),
    ]

    for (player, match, mins, ax, ay, mxs, avs, tact, tech, phys, dec, alrt, pos, notes) in perfs_data:
        session.add(PlayerMatchPerformance(
            player_id=player.id, match_id=match.id,
            minutes_played=mins,
            average_position_x=ax, average_position_y=ay,
            max_speed=mxs, average_speed=avs,
            tactical_score=tact, technical_score=tech,
            physical_score=phys, decision_score=dec,
            alerts_involved=alrt, positive_actions=pos,
            development_notes=notes,
        ))
    session.commit()

    # ── ScoutNotes ────────────────────────────────────────────────────────────
    scout_notes_data = [
        (p_kerem, "Sağ kanatta içeri kesme davranışı çok hızlı. 2. pas kalitesi yüksek.",                8.4, ["progression", "decision"]),
        (p_arda,  "Orta sahada top alma pozisyonlaması iyi. Baskı altında sakin kalabiliyor.",            7.9, ["composure", "positioning"]),
        (p_can,   "Uzun pas isabeti dikkat çekici. Çıkış kararları maç deneyimiyle gelişiyor.",           7.5, ["distribution", "decision"]),
        (p_mert,  "Ceza sahası içi hareket kalitesi yüksek. Bitiricilik tutarlı.",                        8.1, ["finishing", "movement"]),
        (p_emir,  "Savunma hattı liderliği yapıyor. Derin koşu kapama geliştirilmeli.",                   7.2, ["leadership", "defensive_line"]),
    ]

    for (player, note, rating, tags) in scout_notes_data:
        session.add(ScoutNote(
            player_id=player.id,
            scout_id=scout_user.id,
            note=note,
            rating=rating,
            tags_json={"tags": tags},
        ))
    session.commit()


    # ── Reports ───────────────────────────────────────────────────────────────
    reports_data = [
        (m_u15.id, None,       ReportType.MATCH_SUMMARY,      "U15 Kırmızı Takım vs Mavi Spor — Maç Raporu",    "Baskı tetikleyicileri ve geçiş organizasyonundaki gelişim alanları. 6 taktiksel uyarı tespit edildi."),
        (None,     p_can.id,   ReportType.PLAYER_DEVELOPMENT, "Can Öztürk — Oyuncu Gelişim Raporu",             "Uzun pas isabeti ve çıkış kararları ön plana çıkıyor. Gelişim ivmesi: +0.44."),
        (None,     None,       ReportType.SCOUTING,           "U15 Scouting Kısa Liste",                        "Kerem Demir ve Arda Yılmaz transfer listesine alındı. Gelişim ivmesi kriterleri karşılandı."),
        (None,     None,       ReportType.TRAINING,           "Mart 2026 Akademi Gelişim Özeti",                "Tüm takımlar için aylık gelişim özeti. Kompaktlık ve geçiş savunması öncelikli çalışma alanları."),
    ]

    for (mid, pid, rtype, title, summary) in reports_data:
        session.add(Report(
            match_id=mid, player_id=pid,
            report_type=rtype, title=title, summary=summary,
        ))
    session.commit()

    # ── DrillRecommendations ──────────────────────────────────────────────────
    drills_data = [
        (AlertType.BLOCK_GAP_WIDE,          "8v8 Kompakt Blok Oyunu",                    ProblemType.TACTICAL,  "U15", 18, 16, PitchSize.HALF,        DrillDifficulty.MEDIUM, "Savunma ve orta saha bloğu kopukluğunu gidermek için kompakt blok oyunu.",
         [{"tr": "Bloklar arası mesafe 12-15 m aralığında tutulmalı"}, {"tr": "Top tarafına birlikte kayma yapılmalı"}, {"tr": "Top kaybından sonra ilk reaksiyon 5 saniye içinde gelmeli"}]),
        (AlertType.POOR_TRANSITION_DEFENSE, "5 Saniye Karşı Pres Oyunu",                 ProblemType.PHYSICAL,  "U15", 20, 14, PitchSize.HALF,        DrillDifficulty.HARD,   "Geçiş esnasında hızlı defensive reaksiyon ve press trigger.",
         [{"tr": "Top kaybından sonra ilk 5 saniye pres tetikleme"}, {"tr": "Omuz hizası ve doğru açı seçimi"}, {"tr": "Yönlendirme ve ikinci dalga koordinasyonu"}]),
        (AlertType.DEPTH_RUN_OPPORTUNITY,   "Üçüncü Adam Koşusu",                        ProblemType.TACTICAL,  "U15", 16, 12, PitchSize.SMALL_SIDED, DrillDifficulty.MEDIUM, "Derin koşu pozisyonlaması ve pas opsiyonu yaratma.",
         [{"tr": "Üçüncü adam pozisyonlaması defans hattının arkasında"}, {"tr": "Zamanlanmış çalışma ve pas ritmi"}, {"tr": "Defans linesi geçme hareketleri (timing)"}]),
        (AlertType.DEFENSIVE_LINE_BREAK,    "Savunma Çizgisi Senkronizasyonu",           ProblemType.TACTICAL,  "U15", 15,  8, PitchSize.HALF,        DrillDifficulty.HARD,   "Savunma çizgisi disiplini ve hat hizasında kalma öğretimi.",
         [{"tr": "Hat uyumu (4 bek aynı hizada kalma)"}, {"tr": "Savunma arkası kontrol ve offside hareketleri"}, {"tr": "Topla çıkış tekniği (GK ve merkez bek)"}]),
        (AlertType.LACK_OF_SUPPORT_RUN,     "Destek Açısı ve Pas Opsiyonu Oyunu",        ProblemType.TACTICAL,  "U15", 18, 14, PitchSize.SMALL_SIDED, DrillDifficulty.MEDIUM, "Top taşıyıcı için her zaman pas opsiyonu yaratma.",
         [{"tr": "Destek koşusu açı seçimi (30-45 derece)"}, {"tr": "Orta sahadan gelen derinlik"}, {"tr": "Pas ve move kombinasyonları"}]),
    ]

    for (atype, title, ptype, age, dur, cnt, psize, diff, desc, cpts) in drills_data:
        session.add(DrillRecommendation(
            alert_type=atype, title=title, problem_type=ptype,
            age_category=age, duration_minutes=dur, player_count=cnt,
            pitch_size=psize, difficulty=diff,
            description=desc, coaching_points_json=cpts,
        ))
    session.commit()

    print(f"✅ Seed tamamlandı — org: {org.id}, takım: 4, oyuncu: 6, maç: 4, alert: {len(alert_objs)}")


# ── CLI entry ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from app.db.session import engine
    with Session(engine) as s:
        seed_demo_data(s)
