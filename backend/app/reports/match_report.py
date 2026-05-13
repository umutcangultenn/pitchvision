"""
Maç raporu oluşturma modülü.
Taktiksel analiz verilerinden yapılandırılmış rapor üretir.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


# ── Drill mapping ──────────────────────────────────────────────────────────────

DRILL_MAP: Dict[str, Dict[str, Any]] = {
    "block_gap_wide": {
        "title": "8v8 Kompakt Blok Oyunu",
        "description": "Savunma, orta saha ve forvet blokları arasındaki mesafeyi azaltmaya yönelik küçük saha oyunu.",
        "duration_minutes": 20,
        "focus": ["compactness", "block_distance", "team_shape"],
        "coaching_points": [
            "Bloklar arası mesafeyi 15-20m'de tutun",
            "Top kaybında hızla kompakt olun",
            "Orta saha oyuncuları köprü görevi yapın",
        ],
    },
    "defensive_line_break": {
        "title": "Savunma Çizgisi Senkronizasyonu",
        "description": "Savunma oyuncularının hat düzgünlüğünü ve senkronize hareketini geliştirme egzersizi.",
        "duration_minutes": 18,
        "focus": ["defensive_line", "communication", "positioning"],
        "coaching_points": [
            "Sürekli iletişim halinde olun",
            "En yavaş oyuncuya göre hareket edin",
            "Ofsayt tuzağı kurarken beraber çıkın",
        ],
    },
    "transition_slow": {
        "title": "5 Saniye Karşı Pres Oyunu",
        "description": "Top kaybından sonra ilk 5 saniyede agresif baskı ve hızlı geçiş pratiği.",
        "duration_minutes": 15,
        "focus": ["counter_press", "transition_speed", "pressing"],
        "coaching_points": [
            "Top kaybında ilk 5 saniye kritik",
            "En yakın 2 oyuncu hemen baskı uygular",
            "Geride kalanlar kompakt blok oluşturur",
        ],
    },
    "depth_run_opportunity": {
        "title": "Üçüncü Adam Koşusu",
        "description": "Savunma arkasına zamanlanmış koşu ve pas koordinasyonu.",
        "duration_minutes": 20,
        "focus": ["timing", "through_balls", "depth_runs"],
        "coaching_points": [
            "Pas öncesi koşuya başlayın",
            "Ofsayt çizgisini takip edin",
            "İlk dokunuşla kontrolü sağlayın",
        ],
    },
    "compactness_lost": {
        "title": "Destek Açısı ve Pas Opsiyonu Oyunu",
        "description": "Takım kompaktlığını korurken destek koşuları ve pas seçenekleri geliştirme.",
        "duration_minutes": 22,
        "focus": ["support_runs", "passing_options", "compactness"],
        "coaching_points": [
            "Her zaman 2 pas opsiyonu yaratın",
            "Destek açısı 30-45 derece olmalı",
            "Takım genişliği 40m'yi geçmesin",
        ],
    },
}

_ALERT_TO_DRILL = {
    "block_gap_wide": "block_gap_wide",
    "defensive_line_break": "defensive_line_break",
    "transition_slow": "transition_slow",
    "depth_run_opportunity": "depth_run_opportunity",
    "compactness_lost": "compactness_lost",
    # fallback aliases
    "poor_transition_defense": "transition_slow",
    "lack_of_support_run": "compactness_lost",
}


def get_drill_for_alert(alert_type: str) -> Optional[Dict[str, Any]]:
    key = _ALERT_TO_DRILL.get(alert_type)
    if key:
        return {"drill_key": key, **DRILL_MAP[key]}
    return None


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class ReportAlert:
    id: int
    alert_type: str
    timestamp_seconds: float
    confidence: float
    severity: str
    title: str
    description: str
    clip_id: Optional[int] = None
    drill: Optional[Dict[str, Any]] = None


@dataclass
class ReportClip:
    id: int
    title: str
    description: str
    start_time: float
    end_time: float
    tag: str
    alert_id: Optional[int] = None
    player_id: Optional[int] = None


@dataclass
class ReportPlayer:
    id: int
    name: str
    position: str
    minutes_played: int
    tactical_score: float
    technical_score: float
    physical_score: float
    decision_score: float
    alerts_involved: int
    development_notes: str
    max_speed: float


@dataclass
class TeamShapeMetrics:
    team_length: float
    team_width: float
    compactness: float
    defense_midfield_gap: float
    midfield_forward_gap: float
    transition_speed: float


@dataclass
class MatchReport:
    # 1. Kapak
    match_id: int
    team_name: str
    opponent_name: str
    match_date: str
    age_category: str
    score_for: int
    score_against: int
    video_source: str
    calibration_quality: str
    tracking_confidence: float
    generated_at: str

    # 2. Maç özeti
    summary: str

    # 3. En önemli 3 bulgu
    top_findings: List[str]

    # 4. Takım şekli metrikleri
    team_shape: TeamShapeMetrics

    # 5. Taktiksel uyarılar
    alerts: List[ReportAlert]

    # 6. Klipler
    clips: List[ReportClip]

    # 7. Oyuncu performansı
    players: List[ReportPlayer]

    # 8. Antrenman önerileri
    drill_recommendations: List[Dict[str, Any]]

    # 9. Bir sonraki maçta takip edilecek göstergeler
    next_match_indicators: List[str]

    # Etik not
    disclaimer: str = (
        "Bu rapor otomatik analiz adayları içerir. "
        "Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır."
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


# ── Main generator ─────────────────────────────────────────────────────────────

def generate_match_report(
    match_id: int,
    match_data: Dict[str, Any],
    alerts_data: List[Dict[str, Any]],
    clips_data: List[Dict[str, Any]],
    players_data: List[Dict[str, Any]],
    performances_data: List[Dict[str, Any]],
    team_shape_data: Optional[Dict[str, Any]] = None,
) -> MatchReport:
    """
    Maç raporu oluşturur.

    Args:
        match_id: Maç ID'si
        match_data: Maç bilgileri (opponentName, matchDate, scoreFor, scoreAgainst, …)
        alerts_data: Taktiksel uyarılar listesi
        clips_data: Klip listesi
        players_data: Oyuncu listesi
        performances_data: Oyuncu performans verileri
        team_shape_data: Takım şekli metrikleri (opsiyonel, yoksa mock değerler)

    Returns:
        MatchReport: Yapılandırılmış rapor
    """
    # ── 1. Kapak bilgileri ─────────────────────────────────────────────────────
    team_name = match_data.get("teamName", "Takım")
    opponent = match_data.get("opponentName", "Rakip")
    match_date = match_data.get("matchDate", datetime.now().isoformat())
    age_category = match_data.get("ageCategory", "U15")
    score_for = match_data.get("scoreFor", 0)
    score_against = match_data.get("scoreAgainst", 0)
    video_source = match_data.get("videoSource", "file_upload")

    # ── 4. Takım şekli ────────────────────────────────────────────────────────
    ts = team_shape_data or {}
    team_shape = TeamShapeMetrics(
        team_length=ts.get("teamLength", 47.2),
        team_width=ts.get("teamWidth", 42.8),
        compactness=ts.get("compactness", 18.4),
        defense_midfield_gap=ts.get("defenseMidfieldGap", 21.4),
        midfield_forward_gap=ts.get("midfieldForwardGap", 16.8),
        transition_speed=ts.get("transitionSpeed", 4.6),
    )

    # ── 5. Uyarılar ───────────────────────────────────────────────────────────
    alerts: List[ReportAlert] = []
    for a in alerts_data:
        drill = get_drill_for_alert(a.get("alertType", ""))
        alerts.append(
            ReportAlert(
                id=a.get("id", 0),
                alert_type=a.get("alertType", ""),
                timestamp_seconds=a.get("startTime", 0),
                confidence=a.get("confidence", 0.0),
                severity=a.get("severity", "low"),
                title=a.get("title", ""),
                description=a.get("description", ""),
                clip_id=a.get("suggestedClipId"),
                drill=drill,
            )
        )

    # Önem sırasına göre sırala
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda x: (severity_order.get(x.severity, 9), -x.confidence))

    # ── 6. Klipler ────────────────────────────────────────────────────────────
    clips: List[ReportClip] = [
        ReportClip(
            id=c.get("id", 0),
            title=c.get("title", ""),
            description=c.get("description", ""),
            start_time=c.get("startTime", 0),
            end_time=c.get("endTime", 0),
            tag=c.get("tag", ""),
            alert_id=c.get("alertId"),
            player_id=c.get("playerId"),
        )
        for c in clips_data
    ]

    # ── 7. Oyuncu performansı ─────────────────────────────────────────────────
    perf_by_player = {p.get("playerId"): p for p in performances_data}
    players: List[ReportPlayer] = []
    for pl in players_data:
        pid = pl.get("id")
        perf = perf_by_player.get(pid, {})
        players.append(
            ReportPlayer(
                id=pid,
                name=f"{pl.get('firstName', '')} {pl.get('lastName', '')}".strip(),
                position=pl.get("position", ""),
                minutes_played=perf.get("minutesPlayed", 0),
                tactical_score=perf.get("tacticalScore") or pl.get("tacticalScore", 5.0),
                technical_score=perf.get("technicalScore") or pl.get("technicalScore", 5.0),
                physical_score=perf.get("physicalScore") or pl.get("physicalScore", 5.0),
                decision_score=perf.get("decisionScore") or pl.get("decisionScore", 5.0),
                alerts_involved=perf.get("alertsInvolved", 0),
                development_notes=perf.get("developmentNotes", ""),
                max_speed=perf.get("maxSpeed", 0.0),
            )
        )

    # ── 8. Antrenman önerileri ────────────────────────────────────────────────
    seen_drills: set = set()
    drill_recommendations: List[Dict[str, Any]] = []
    for alert in alerts:
        if alert.drill and alert.drill["drill_key"] not in seen_drills:
            seen_drills.add(alert.drill["drill_key"])
            drill_recommendations.append({
                "triggered_by": alert.alert_type,
                "triggered_by_title": alert.title,
                **alert.drill,
            })

    # ── 2. Maç özeti ──────────────────────────────────────────────────────────
    result_str = (
        "galibiyet" if score_for > score_against
        else "beraberlik" if score_for == score_against
        else "mağlubiyet"
    )
    high_alerts = [a for a in alerts if a.severity in ("high", "critical")]
    summary = (
        f"{team_name} - {opponent} maçı {score_for}-{score_against} {result_str} ile sonuçlandı. "
        f"Analiz {len(alerts)} taktiksel uyarı tespit etti; "
        f"bunların {len(high_alerts)} tanesi yüksek/kritik önem taşıyor. "
        f"Takım şekli metrikleri ortalama {team_shape.compactness:.1f}m kompaktlık gösterdi."
    )

    # ── 3. En önemli 3 bulgu ──────────────────────────────────────────────────
    top_findings = _derive_top_findings(alerts, team_shape, players)

    # ── 9. Bir sonraki maçta takip edilecek göstergeler ───────────────────────
    next_match_indicators = _derive_next_match_indicators(alerts, team_shape)

    return MatchReport(
        match_id=match_id,
        team_name=team_name,
        opponent_name=opponent,
        match_date=match_date,
        age_category=age_category,
        score_for=score_for,
        score_against=score_against,
        video_source=video_source,
        calibration_quality=match_data.get("calibrationQuality", "good"),
        tracking_confidence=match_data.get("trackingConfidence", 0.94),
        generated_at=datetime.now().isoformat(),
        summary=summary,
        top_findings=top_findings,
        team_shape=team_shape,
        alerts=alerts,
        clips=clips,
        players=players,
        drill_recommendations=drill_recommendations,
        next_match_indicators=next_match_indicators,
    )


def _derive_top_findings(
    alerts: List[ReportAlert],
    team_shape: TeamShapeMetrics,
    players: List[ReportPlayer],
) -> List[str]:
    findings = []

    # En yüksek güvenli uyarı
    if alerts:
        top = alerts[0]
        findings.append(
            f"En kritik uyarı: '{top.title}' "
            f"(%{int(top.confidence * 100)} güven, {top.severity} önem)"
        )

    # Kompaktlık değerlendirmesi
    if team_shape.compactness > 20:
        findings.append(
            f"Takım kompaktlığı {team_shape.compactness:.1f}m ile eşiğin üzerinde — "
            "bloklar arası mesafe azaltılmalı."
        )
    else:
        findings.append(
            f"Takım kompaktlığı {team_shape.compactness:.1f}m ile iyi seviyede."
        )

    # En iyi performans gösteren oyuncu
    if players:
        best = max(players, key=lambda p: (p.tactical_score + p.technical_score) / 2)
        avg = (best.tactical_score + best.technical_score) / 2
        findings.append(
            f"En yüksek taktik+teknik ortalama: {best.name} ({avg:.1f}/10)"
        )

    return findings[:3]


def _derive_next_match_indicators(
    alerts: List[ReportAlert],
    team_shape: TeamShapeMetrics,
) -> List[str]:
    indicators = []
    alert_types = {a.alert_type for a in alerts}

    if "defensive_line_break" in alert_types:
        indicators.append("Savunma hattı düzgünlüğü — hat sapması < 4m hedefi")
    if "block_gap_wide" in alert_types:
        indicators.append("Bloklar arası mesafe — savunma-orta saha < 25m hedefi")
    if "transition_slow" in alert_types:
        indicators.append("Geçiş hızı — top kazanımından 5 saniyede ileri bölge")
    if "depth_run_opportunity" in alert_types:
        indicators.append("Derin koşu zamanlaması — ofsayt sayısını azalt")
    if "compactness_lost" in alert_types:
        indicators.append("Takım kompaktlığı — ortalama mesafe < 20m hedefi")

    # Genel göstergeler
    indicators.append(f"Geçiş hızı hedefi: ≥ {team_shape.transition_speed + 0.5:.1f} m/s")
    indicators.append("Savunma-orta saha mesafesi: < 20m")

    return indicators[:5]
