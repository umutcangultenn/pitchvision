#!/usr/bin/env python
"""
Wrapper: demo verisini veritabanına yükler.

Kullanım:
    # Proje kökünden (pitchvision-lite/):
    cd backend
    python scripts/seed_demo.py

    # Docker Compose ile:
    docker compose exec backend python scripts/seed_demo.py
"""
import sys
from pathlib import Path

# backend/ dizinini Python path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session
from app.db.session import engine
from app.db.seed import seed_demo_data

if __name__ == "__main__":
    print("🌱 Demo seed başlatılıyor — Anadolu Akademi...")
    with Session(engine) as session:
        seed_demo_data(session)
    print("✅ Tamamlandı.")
