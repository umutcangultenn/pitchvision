from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from app.analytics.types import AlertSeverity, AlertType, TacticalAlert

Difficulty = Literal["easy", "medium", "hard"]


@dataclass
class DrillSpec:
    name: str
    duration_minutes: int
    difficulty: Difficulty
    focus_area: str
    equipment: list[str] = field(default_factory=list)


DRILL_DATABASE: dict[AlertType, list[DrillSpec]] = {
    AlertType.DEFENSIVE_LINE_BREAK: [
        DrillSpec("Hat senkronizasyonu", 18, "medium", "defensive_line", ["koniler", "raket"]),
        DrillSpec("Savunma çizgisi 4v4", 25, "hard", "defensive_line", ["toplar", "kale"]),
        DrillSpec("Kısa mesafe hat oyunu", 12, "easy", "defensive_line", ["koniler"]),
    ],
    AlertType.BLOCK_GAP_WIDE: [
        DrillSpec("Kompakt blok 8v8", 20, "medium", "compactness", ["toplar", "koniler"]),
        DrillSpec("Blok mesafesi pres", 10, "easy", "pressing", ["koniler"]),
        DrillSpec("Geçiş savunması", 15, "medium", "transition", ["toplar"]),
    ],
    AlertType.COMPACTNESS_LOST: [
        DrillSpec("Dar alan oyunu", 15, "easy", "compactness", ["koniler"]),
        DrillSpec("Destek açısı pas", 22, "medium", "passing", ["toplar"]),
    ],
    AlertType.TRANSITION_SLOW: [
        DrillSpec("3 saniye karşı pres", 12, "easy", "pressing", ["koniler"]),
        DrillSpec("Hızlı geçiş 6v6", 30, "hard", "transition", ["toplar", "kale"]),
        DrillSpec("Geçiş rondo", 14, "medium", "transition", ["toplar"]),
    ],
}


def get_drill_recommendations(
    alert: TacticalAlert,
    team_level: str = "professional",
    available_time: int = 60,
    player_count: int = 11,
) -> list[DrillSpec]:
    drills = list(DRILL_DATABASE.get(alert.alert_type, []))
    out: list[DrillSpec] = []
    for d in drills:
        if d.duration_minutes > available_time:
            continue
        if team_level == "youth" and d.difficulty == "hard":
            continue
        out.append(d)
        if len(out) >= 3:
            break
    return out


def create_training_session(
    alerts: list[TacticalAlert],
    session_duration: int = 90,
    team_level: str = "professional",
) -> dict[str, Any]:
    sev_order = {
        AlertSeverity.CRITICAL: 0,
        AlertSeverity.HIGH: 1,
        AlertSeverity.MEDIUM: 2,
        AlertSeverity.LOW: 3,
    }
    ranked = sorted(alerts, key=lambda a: (sev_order[a.severity], -a.confidence))
    main: list[dict[str, Any]] = []
    for a in ranked[:5]:
        for d in get_drill_recommendations(a, team_level=team_level, available_time=session_duration - 20):
            main.append(
                {
                    "alert_type": a.alert_type.value,
                    "drill": d.name,
                    "duration": d.duration_minutes,
                }
            )
            break
    return {
        "warm_up": {"duration": 10, "description": "Dinamik ısınma"},
        "main_drills": main,
        "cool_down": {"duration": 8, "description": "Soğuma"},
        "total_duration": session_duration,
    }


def get_drill_by_focus_area(focus: str) -> list[DrillSpec]:
    out: list[DrillSpec] = []
    for specs in DRILL_DATABASE.values():
        for d in specs:
            if d.focus_area == focus:
                out.append(d)
    return out


def get_equipment_list(drills: list[DrillSpec]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for d in drills:
        for e in d.equipment:
            if e not in seen:
                seen.add(e)
                ordered.append(e)
    return ordered
