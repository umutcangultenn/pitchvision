from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables
from app.api import auth, teams, matches, players, analysis, reports
from app.api import segments, engine_events, analyst_events, comparison_api, ai_summary
from app.api import scouting, drills
from app.api import statsbomb
from app.api import passport
from app.api import video_processing
from app.api.tactical_analytics import router as tactical_router

# Import all models so SQLModel registers them before create_db_and_tables
import app.models  # noqa: F401 — triggers __init__.py which imports all models

app = FastAPI(
    title="PitchVision Lite API",
    description="Futbol analiz platformu API",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(players.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

# --- Tactical Engine Upgrade Routers ---
app.include_router(segments.router, prefix="/api")
app.include_router(engine_events.router, prefix="/api")
app.include_router(analyst_events.router, prefix="/api")
app.include_router(comparison_api.router, prefix="/api")
app.include_router(ai_summary.router, prefix="/api")

# --- Scouting & Drills Routers ---
app.include_router(scouting.router, prefix="/api")
app.include_router(drills.router, prefix="/api")

# --- Phase 3: StatsBomb Integration ---
app.include_router(statsbomb.router, prefix="/api")

# --- Player Passport ---
app.include_router(passport.router, prefix="/api")

# --- Video Processing ---
app.include_router(video_processing.router)

# --- Tactical Analytics Engine ---
app.include_router(tactical_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "PitchVision Lite API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
