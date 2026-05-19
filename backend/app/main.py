from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables
from app.api import auth, teams, matches, players, analysis
from app.api import segments, engine_events, analyst_events, comparison_api, ai_summary
# from app.api.tactical_analytics import router as tactical_router

app = FastAPI(
    title="PitchVision Lite API",
    description="Futbol analiz platformu API",
    version="1.0.0"
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

# --- Tactical Engine Upgrade Routers ---
app.include_router(segments.router, prefix="/api")
app.include_router(engine_events.router, prefix="/api")
app.include_router(analyst_events.router, prefix="/api")
app.include_router(comparison_api.router, prefix="/api")
app.include_router(ai_summary.router, prefix="/api")
# app.include_router(tactical_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "PitchVision Lite API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
