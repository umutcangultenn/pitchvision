from fastapi import APIRouter

from app.api.routes import (
    alerts,
    analytics,
    auth,
    calibration,
    clips,
    drills,
    matches,
    organizations,
    players,
    reports,
    saas,
    scouting,
    settings,
    teams,
    videos,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(teams.router)
api_router.include_router(players.router)
api_router.include_router(matches.router)
api_router.include_router(videos.router)
api_router.include_router(calibration.router)
api_router.include_router(analytics.router)
api_router.include_router(alerts.router)
api_router.include_router(clips.router)
api_router.include_router(reports.router)
api_router.include_router(scouting.router)
api_router.include_router(drills.router)
api_router.include_router(settings.router)
api_router.include_router(saas.router)
