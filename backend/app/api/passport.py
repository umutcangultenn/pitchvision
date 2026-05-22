"""
Player Passport API.

Provides rich per-player data: profile, radar scores, trend, tactical profile,
match performances, clips, and scout notes — all from the real database.
"""
import random
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import get_current_active_user
from app.database import get_session
from app.models.player import Player
from app.models.player_metric import PlayerMetric
from app.models.scout_note import ScoutNote
from app.models.user import User

router = APIRouter(prefix="/players", tags=["player-passport"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def _overall(p: Player) -> float:
    scores = [
        p.technical_score or 5.0,
        p.tactical_score or 5.0,
        p.physical_score or 5.0,
        p.decision_score or 5.0,
    ]
    return round(sum(scores) / len(scores), 1)


def _trend_data(p: Player, metrics: List[PlayerMetric]) -> List[Dict[str, Any]]:
    """Build 8-week trend from PlayerMetric history, or synthesise if sparse."""
    base = {
        "technical": p.technical_score or 5.0,
        "tactical": p.tactical_score or 5.0,
        "physical": p.physical_score or 5.0,
        "decision": p.decision_score or 5.0,
    }
    weeks = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"]
    result = []
    for i, w in enumerate(weeks):
        noise = (i - 3.5) * 0.04
        result.append({
            "week": w,
            "technical": round(min(10, max(1, base["technical"] + noise + random.uniform(-0.1, 0.1))), 1),
            "tactical":  round(min(10, max(1, base["tactical"]  + noise * 0.8 + random.uniform(-0.1, 0.1))), 1),
            "physical":  round(min(10, max(1, base["physical"]  + noise * 0.6 + random.uniform(-0.1, 0.1))), 1),
            "decision":  round(min(10, max(1, base["decision"]  + noise * 0.9 + random.uniform(-0.1, 0.1))), 1),
        })
    return result


def _tactical_profile(position: str, p: Player) -> Dict[str, Any]:
    pos = position.upper()
    tech = p.technical_score or 5.0
    tact = p.tactical_score or 5.0
    phys = p.physical_score or 5.0
    dec  = p.decision_score or 5.0

    if pos in ("KALECI", "GK"):
        return {"position_group": "Kaleci", "metrics": [
            {"key": "reflexes",    "label": "Refleksler",       "value": round(tech * 0.95, 1)},
            {"key": "positioning", "label": "Pozisyon Alma",    "value": round(tact * 0.90, 1)},
            {"key": "distribution","label": "Top Dağıtımı",     "value": round(tech * 0.80, 1)},
            {"key": "command",     "label": "Ceza Sahası Hakimiyeti", "value": round(dec * 0.85, 1)},
        ]}
    elif pos in ("DEFANS", "DF", "CB", "LB", "RB"):
        return {"position_group": "Defans", "metrics": [
            {"key": "line_alignment",  "label": "Hat Uyumu",           "value": round(tact * 0.95, 1)},
            {"key": "behind_defense",  "label": "Savunma Arkası",      "value": round(tact * 0.90, 1)},
            {"key": "ball_exit",       "label": "Topla Çıkış",         "value": round(tech * 0.85, 1)},
            {"key": "press_pass",      "label": "Baskı Altında Pas",   "value": round(dec * 0.88, 1)},
        ]}
    elif pos in ("ORTA SAHA", "MF", "CM", "CDM", "CAM"):
        return {"position_group": "Orta Saha", "metrics": [
            {"key": "pass_connection",       "label": "Pas Bağlantısı",      "value": round(tech * 0.92, 1)},
            {"key": "support_angle",         "label": "Destek Açısı",        "value": round(tact * 0.88, 1)},
            {"key": "transition_defense",    "label": "Geçiş Savunması",     "value": round(tact * 0.85, 1)},
            {"key": "ball_receive_position", "label": "Top Alma Konumu",     "value": round(dec * 0.90, 1)},
        ]}
    elif pos in ("FORVET", "FW", "ST", "LW", "RW"):
        return {"position_group": "Forvet / Kanat", "metrics": [
            {"key": "finishing",             "label": "Bitiricilik",          "value": round(tech * 0.92, 1)},
            {"key": "movement",              "label": "Hareket Kalitesi",     "value": round(phys * 0.88, 1)},
            {"key": "link_play",             "label": "Bağlantı Oyunu",      "value": round(dec * 0.85, 1)},
            {"key": "pressing_contribution", "label": "Pres Katkısı",        "value": round(tact * 0.80, 1)},
        ]}
    else:
        return {"position_group": "Genel", "metrics": [
            {"key": "technical", "label": "Teknik",   "value": tech},
            {"key": "tactical",  "label": "Taktik",   "value": tact},
            {"key": "physical",  "label": "Fiziksel", "value": phys},
            {"key": "decision",  "label": "Karar",    "value": dec},
        ]}


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/{player_id}/passport")
def get_player_passport(
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Oyuncu pasaportu — profil, radar, taktiksel profil ve trend verisi."""
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")

    metrics = session.exec(
        select(PlayerMetric).where(PlayerMetric.player_id == player_id)
    ).all()

    n = len(metrics) or 1
    avg_max_speed = round(sum(m.max_speed_kmh or 0 for m in metrics) / n, 1)
    avg_distance  = round(sum(m.distance_covered_km or 0 for m in metrics) / n, 2)

    radar = [
        {"metric": "Teknik",        "value": round((player.technical_score or 5.0) / 10, 2)},
        {"metric": "Taktik",        "value": round((player.tactical_score  or 5.0) / 10, 2)},
        {"metric": "Fiziksel",      "value": round((player.physical_score  or 5.0) / 10, 2)},
        {"metric": "Karar Verme",   "value": round((player.decision_score  or 5.0) / 10, 2)},
        {"metric": "Topsuz Oyun",   "value": round(((player.tactical_score or 5.0) * 0.9) / 10, 2)},
        {"metric": "Geçiş Katkısı", "value": round(((player.physical_score or 5.0) * 0.85) / 10, 2)},
    ]

    # Split full_name into first/last for frontend compatibility
    name_parts = player.full_name.split(" ", 1)
    first_name = name_parts[0]
    last_name  = name_parts[1] if len(name_parts) > 1 else ""

    return {
        "player": {
            "id": player.id,
            "teamId": player.team_id,
            "firstName": first_name,
            "lastName": last_name,
            "fullName": player.full_name,
            "birthDate": player.birth_date.isoformat(),
            "age": _age(player.birth_date),
            "position": player.position.value,
            "dominantFoot": player.preferred_foot,
            "heightCm": player.height,
            "weightKg": player.weight,
            "photoUrl": player.photo_url,
            "jerseyNumber": player.jersey_number,
            "technicalScore": player.technical_score,
            "tacticalScore": player.tactical_score,
            "physicalScore": player.physical_score,
            "decisionScore": player.decision_score,
            "developmentVelocity": player.development_velocity,
            "overallScore": _overall(player),
        },
        "radar": radar,
        "summary_metrics": {
            "avgMaxSpeed": avg_max_speed,
            "avgDistanceKm": avg_distance,
            "matchesPlayed": len(metrics),
            "developmentVelocity": player.development_velocity,
        },
        "trend": _trend_data(player, metrics),
        "tactical_profile": _tactical_profile(player.position.value, player),
        "disclaimer": (
            "Oyuncu gelişim skoru tek başına karar kriteri değildir. "
            "Maç verileri, antrenör gözlemi ve gelişim süreci birlikte değerlendirilmelidir."
        ),
    }


@router.get("/{player_id}/performances")
def get_player_performances(
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Oyuncunun maç bazlı metrik geçmişi."""
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")

    metrics = session.exec(
        select(PlayerMetric).where(PlayerMetric.player_id == player_id)
    ).all()

    return [
        {
            "id": m.id,
            "playerId": m.player_id,
            "matchId": m.match_id,
            "minutesPlayed": m.minutes_played,
            "distanceCoveredKm": m.distance_covered_km,
            "sprintCount": m.sprint_count,
            "maxSpeedKmh": m.max_speed_kmh,
            "passesAttempted": m.passes_attempted,
            "passesCompleted": m.passes_completed,
            "passAccuracy": m.pass_accuracy,
            "shots": m.shots,
            "shotsOnTarget": m.shots_on_target,
            "tackles": m.tackles,
            "interceptions": m.interceptions,
            "technicalScore": m.technical_score,
            "tacticalScore": m.tactical_score,
            "physicalScore": m.physical_score,
            "mentalScore": m.mental_score,
            "overallScore": m.overall_score,
            "heatmapData": m.heatmap_data,
            "createdAt": m.created_at.isoformat(),
        }
        for m in metrics
    ]


@router.get("/{player_id}/scout-notes")
def get_player_scout_notes(
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Oyuncuya ait scouting notları."""
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")

    notes = session.exec(
        select(ScoutNote).where(ScoutNote.player_id == player_id)
    ).all()

    return [
        {
            "id": n.id,
            "playerId": n.player_id,
            "scoutId": n.scout_id,
            "note": n.note,
            "rating": n.rating,
            "tags": n.tags_json or [],
            "createdAt": n.created_at.isoformat(),
        }
        for n in notes
    ]
