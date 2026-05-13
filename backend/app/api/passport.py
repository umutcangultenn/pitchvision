"""
Player Passport API endpoints.
Provides rich player data for the passport view.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import date, datetime
import random

router = APIRouter(prefix="/api/players", tags=["player-passport"])


# ── helpers ────────────────────────────────────────────────────────────────────

def _age(birth_date_str: str) -> int:
    try:
        bd = datetime.fromisoformat(birth_date_str.replace("Z", "")).date()
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except Exception:
        return 0


def _overall(p: Dict[str, Any]) -> float:
    scores = [
        p.get("technicalScore", 5.0),
        p.get("tacticalScore", 5.0),
        p.get("physicalScore", 5.0),
        p.get("decisionScore", 5.0),
    ]
    return round(sum(scores) / len(scores), 1)


# ── Demo data store (mirrors frontend demo.ts) ─────────────────────────────────

DEMO_PLAYERS: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1, "organizationId": 1, "teamId": 1,
        "firstName": "Ayşe", "lastName": "Demir",
        "birthDate": "2010-03-15", "position": "CM",
        "dominantFoot": "right", "heightCm": 163, "weightKg": 54,
        "technicalScore": 7.2, "tacticalScore": 7.0,
        "physicalScore": 6.6, "decisionScore": 6.9,
        "developmentVelocity": 0.42,
        "teamName": "U15 Kırmızı Takım",
    },
    2: {
        "id": 2, "organizationId": 1, "teamId": 1,
        "firstName": "Kaan", "lastName": "Yılmaz",
        "birthDate": "2010-09-02", "position": "LW",
        "dominantFoot": "left", "heightCm": 170, "weightKg": 60,
        "technicalScore": 7.8, "tacticalScore": 7.1,
        "physicalScore": 7.0, "decisionScore": 7.3,
        "developmentVelocity": 0.61,
        "teamName": "U15 Kırmızı Takım",
    },
    3: {
        "id": 3, "organizationId": 1, "teamId": 1,
        "firstName": "Efe", "lastName": "Çelik",
        "birthDate": "2011-01-24", "position": "CB",
        "dominantFoot": "right", "heightCm": 178, "weightKg": 70,
        "technicalScore": 6.4, "tacticalScore": 7.6,
        "physicalScore": 7.2, "decisionScore": 7.0,
        "developmentVelocity": 0.55,
        "teamName": "U15 Kırmızı Takım",
    },
}

DEMO_PERFORMANCES: Dict[int, List[Dict[str, Any]]] = {
    1: [
        {"id": 7201, "playerId": 1, "matchId": 1001, "opponentName": "Beyazgöl Spor",
         "matchDate": "2026-04-12", "minutesPlayed": 68,
         "averagePositionX": 0.48, "averagePositionY": 0.55,
         "maxSpeed": 32.4, "averageSpeed": 22.1,
         "tacticalScore": 7.0, "technicalScore": 7.2,
         "physicalScore": 6.5, "decisionScore": 6.9,
         "alertsInvolved": 1, "positiveActions": 18,
         "developmentNotes": "Orta blok geçişlerinde ilk hamle kalitesi iyileştirilmeli."},
        {"id": 7203, "playerId": 1, "matchId": 1002, "opponentName": "Kuzey Koleji",
         "matchDate": "2026-04-26", "minutesPlayed": 72,
         "averagePositionX": 0.50, "averagePositionY": 0.52,
         "maxSpeed": 31.8, "averageSpeed": 21.5,
         "tacticalScore": 7.2, "technicalScore": 7.4,
         "physicalScore": 6.7, "decisionScore": 7.1,
         "alertsInvolved": 0, "positiveActions": 21,
         "developmentNotes": "Pas bağlantısı güçlendi."},
    ],
    2: [
        {"id": 7202, "playerId": 2, "matchId": 1001, "opponentName": "Beyazgöl Spor",
         "matchDate": "2026-04-12", "minutesPlayed": 74,
         "averagePositionX": 0.62, "averagePositionY": 0.44,
         "maxSpeed": 35.1, "averageSpeed": 23.7,
         "tacticalScore": 7.1, "technicalScore": 7.8,
         "physicalScore": 7.0, "decisionScore": 7.3,
         "alertsInvolved": 1, "positiveActions": 24,
         "developmentNotes": "Kanat çizgisi ile iç koridor arasındaki seçim daha erken tetiklenmeli."},
    ],
    3: [
        {"id": 7204, "playerId": 3, "matchId": 1001, "opponentName": "Beyazgöl Spor",
         "matchDate": "2026-04-12", "minutesPlayed": 80,
         "averagePositionX": 0.22, "averagePositionY": 0.50,
         "maxSpeed": 30.2, "averageSpeed": 20.8,
         "tacticalScore": 7.6, "technicalScore": 6.4,
         "physicalScore": 7.2, "decisionScore": 7.0,
         "alertsInvolved": 1, "positiveActions": 15,
         "developmentNotes": "Savunma hattı senkronizasyonu geliştirilmeli."},
    ],
}

DEMO_CLIPS: Dict[int, List[Dict[str, Any]]] = {
    2: [
        {"id": 9001, "matchId": 1001, "playerId": 2,
         "title": "Kanattan yarım alan kırılımı",
         "description": "Top kazanımı sonrası 2. pasla içeri giriş.",
         "startTime": 1234, "endTime": 1289, "tag": "transition"},
    ],
    1: [
        {"id": 9002, "matchId": 1001, "playerId": 1,
         "title": "Baskıdan şut öncesi pas",
         "description": "İlk temas sonrası 2. pasla şut bölgesine giriş.",
         "startTime": 520, "endTime": 610, "tag": "pressing"},
    ],
    3: [
        {"id": 9003, "matchId": 1001, "playerId": 3,
         "title": "Duel sonrası ikinci top",
         "description": "Yüksek tempo duel sonrası ikinci top kazanımı.",
         "startTime": 1840, "endTime": 1910, "tag": "duel"},
    ],
}

DEMO_SCOUT_NOTES: Dict[int, List[Dict[str, Any]]] = {
    2: [
        {"id": 8001, "playerId": 2, "scoutId": 42,
         "scoutName": "Mehmet Koç",
         "note": "İç koridora yönelme davranışı çok hızlı. 2. pas kalitesi yüksek.",
         "rating": 8.4, "tags": ["progression", "decision"],
         "createdAt": "2026-04-13T10:00:00Z"},
    ],
    1: [
        {"id": 8002, "playerId": 1, "scoutId": 42,
         "scoutName": "Mehmet Koç",
         "note": "Orta sahada top alma pozisyonu gelişiyor. Baskı altında sakin.",
         "rating": 7.8, "tags": ["positioning", "composure"],
         "createdAt": "2026-04-13T10:30:00Z"},
    ],
    3: [],
}


def _trend_data(base_scores: Dict[str, float]) -> List[Dict[str, Any]]:
    """Generate 8-week trend data with slight variation."""
    weeks = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"]
    result = []
    for i, w in enumerate(weeks):
        noise = (i - 3.5) * 0.04
        result.append({
            "week": w,
            "technical": round(min(10, max(1, base_scores["technical"] + noise + random.uniform(-0.1, 0.1))), 1),
            "tactical": round(min(10, max(1, base_scores["tactical"] + noise * 0.8 + random.uniform(-0.1, 0.1))), 1),
            "physical": round(min(10, max(1, base_scores["physical"] + noise * 0.6 + random.uniform(-0.1, 0.1))), 1),
            "decision": round(min(10, max(1, base_scores["decision"] + noise * 0.9 + random.uniform(-0.1, 0.1))), 1),
        })
    return result


def _tactical_profile(position: str, p: Dict[str, Any]) -> Dict[str, Any]:
    """Return position-specific tactical metrics."""
    pos = position.upper()

    if pos in ("CB", "LB", "RB", "SW"):
        return {
            "position_group": "Stoper / Bek",
            "metrics": [
                {"key": "line_alignment",       "label": "Hat Uyumu",              "value": round(p["tacticalScore"] * 0.95, 1)},
                {"key": "behind_defense",        "label": "Savunma Arkası Kontrol", "value": round(p["tacticalScore"] * 0.90, 1)},
                {"key": "ball_exit",             "label": "Topla Çıkış",            "value": round(p["technicalScore"] * 0.85, 1)},
                {"key": "press_pass",            "label": "Baskı Altında Pas",      "value": round(p["decisionScore"] * 0.88, 1)},
            ],
        }
    elif pos in ("CM", "CDM", "CAM", "DM"):
        return {
            "position_group": "Merkez Orta Saha",
            "metrics": [
                {"key": "pass_connection",       "label": "Pas Bağlantısı",         "value": round(p["technicalScore"] * 0.92, 1)},
                {"key": "support_angle",         "label": "Destek Açısı",           "value": round(p["tacticalScore"] * 0.88, 1)},
                {"key": "transition_defense",    "label": "Geçiş Savunması",        "value": round(p["tacticalScore"] * 0.85, 1)},
                {"key": "ball_receive_position", "label": "Top Alma Konumu",        "value": round(p["decisionScore"] * 0.90, 1)},
            ],
        }
    elif pos in ("LW", "RW", "LM", "RM", "WF"):
        return {
            "position_group": "Kanat",
            "metrics": [
                {"key": "depth_run",             "label": "Derin Koşu",             "value": round(p["physicalScore"] * 0.90, 1)},
                {"key": "width_maintenance",     "label": "Genişlik Koruma",        "value": round(p["tacticalScore"] * 0.85, 1)},
                {"key": "one_v_one",             "label": "1v1 Katkı",              "value": round(p["technicalScore"] * 0.88, 1)},
                {"key": "defensive_return",      "label": "Geri Dönüş Savunması",   "value": round(p["physicalScore"] * 0.82, 1)},
            ],
        }
    elif pos in ("ST", "CF", "SS"):
        return {
            "position_group": "Forvet",
            "metrics": [
                {"key": "finishing",             "label": "Bitiricilik",            "value": round(p["technicalScore"] * 0.92, 1)},
                {"key": "movement",              "label": "Hareket Kalitesi",       "value": round(p["physicalScore"] * 0.88, 1)},
                {"key": "link_play",             "label": "Bağlantı Oyunu",         "value": round(p["decisionScore"] * 0.85, 1)},
                {"key": "pressing_contribution", "label": "Pres Katkısı",           "value": round(p["tacticalScore"] * 0.80, 1)},
            ],
        }
    else:
        return {
            "position_group": "Genel",
            "metrics": [
                {"key": "technical",  "label": "Teknik",  "value": p["technicalScore"]},
                {"key": "tactical",   "label": "Taktik",  "value": p["tacticalScore"]},
                {"key": "physical",   "label": "Fiziksel","value": p["physicalScore"]},
                {"key": "decision",   "label": "Karar",   "value": p["decisionScore"]},
            ],
        }


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/{player_id}/passport")
async def get_player_passport(player_id: int):
    """
    Oyuncu pasaportu — profil, radar, taktiksel profil ve trend verisi.
    """
    p = DEMO_PLAYERS.get(player_id)
    if not p:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")

    perfs = DEMO_PERFORMANCES.get(player_id, [])
    avg_max_speed = round(sum(x.get("maxSpeed", 0) for x in perfs) / max(len(perfs), 1), 1)
    avg_speed = round(sum(x.get("averageSpeed", 0) for x in perfs) / max(len(perfs), 1), 1)
    total_positive = sum(x.get("positiveActions", 0) for x in perfs)
    total_alerts = sum(x.get("alertsInvolved", 0) for x in perfs)

    radar = [
        {"metric": "Teknik",         "value": round(p["technicalScore"] / 10, 2)},
        {"metric": "Taktik",         "value": round(p["tacticalScore"] / 10, 2)},
        {"metric": "Fiziksel",       "value": round(p["physicalScore"] / 10, 2)},
        {"metric": "Karar Verme",    "value": round(p["decisionScore"] / 10, 2)},
        {"metric": "Topsuz Oyun",    "value": round((p["tacticalScore"] * 0.9) / 10, 2)},
        {"metric": "Geçiş Katkısı",  "value": round((p["physicalScore"] * 0.85) / 10, 2)},
    ]

    trend = _trend_data({
        "technical": p["technicalScore"],
        "tactical":  p["tacticalScore"],
        "physical":  p["physicalScore"],
        "decision":  p["decisionScore"],
    })

    tactical_profile = _tactical_profile(p["position"], p)

    return {
        "player": {
            **p,
            "age": _age(p["birthDate"]),
            "overallScore": _overall(p),
        },
        "radar": radar,
        "summary_metrics": {
            "avgMaxSpeed": avg_max_speed,
            "avgSpeed": avg_speed,
            "totalPositiveActions": total_positive,
            "totalAlertsInvolved": total_alerts,
            "matchesPlayed": len(perfs),
            "developmentVelocity": p["developmentVelocity"],
        },
        "trend": trend,
        "tactical_profile": tactical_profile,
        "disclaimer": (
            "Oyuncu gelişim skoru tek başına karar kriteri değildir. "
            "Maç verileri, antrenör gözlemi ve gelişim süreci birlikte değerlendirilmelidir."
        ),
    }


@router.get("/{player_id}/performances")
async def get_player_performances(player_id: int):
    """Oyuncunun maç performans geçmişi."""
    if player_id not in DEMO_PLAYERS:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")
    return DEMO_PERFORMANCES.get(player_id, [])


@router.get("/{player_id}/clips")
async def get_player_clips(player_id: int):
    """Oyuncuya ait klipler."""
    if player_id not in DEMO_PLAYERS:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")
    return DEMO_CLIPS.get(player_id, [])


@router.get("/{player_id}/scout-notes")
async def get_player_scout_notes(player_id: int):
    """Oyuncuya ait scouting notları."""
    if player_id not in DEMO_PLAYERS:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")
    return DEMO_SCOUT_NOTES.get(player_id, [])
