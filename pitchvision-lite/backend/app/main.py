from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlmodel import SQLModel, Session

import app.models  # noqa: F401
from app.api.router import api_router
from app.core.config import get_settings
from app.db.seed import seed_demo_data
from app.db.session import engine, get_session

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

_origins = settings.cors_origin_list()
# allow_credentials=True ile allow_origins=["*"] birlikte kullanılamaz (Starlette kuralı).
_allow_credentials = _origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # MVP kolaylığı: tablo yoksa oluştur, demo veriyi idempotent şekilde yükle.
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_demo_data(session)


app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "pitchvision-lite-api"}


@app.get("/db-check")
def db_check(session: Session = Depends(get_session)) -> dict[str, str]:
    """Veritabanı oturumunun açılabildiğini doğrular (MVP smoke test)."""
    session.execute(text("SELECT 1"))
    return {"database": "reachable"}
