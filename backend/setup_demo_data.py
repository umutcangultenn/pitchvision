"""
Setup demo data: creates the default dev user + team.

Run from backend/ directory:
    python setup_demo_data.py

Credentials created:
    Email:    dev@pitchvision.local
    Password: demo12345
"""
import sys
from pathlib import Path

# Ensure app package is importable when run from backend/
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, create_engine, select
from app.models.user import User
from app.models.team import Team
from app.auth import get_password_hash
from app.config import settings

engine = create_engine(settings.DATABASE_URL)


def setup_demo_data() -> None:
    with Session(engine) as session:
        # ── User ──────────────────────────────────────────────────────────────
        existing_user = session.exec(
            select(User).where(User.email == "dev@pitchvision.local")
        ).first()

        if existing_user:
            print(f"✅ Demo user already exists (ID: {existing_user.id})")
            user_id = existing_user.id
        else:
            demo_user = User(
                email="dev@pitchvision.local",
                full_name="Development User",
                hashed_password=get_password_hash("demo12345"),
                is_active=True,
                role="coach",
                organization="PitchVision Dev",
            )
            session.add(demo_user)
            session.commit()
            session.refresh(demo_user)
            user_id = demo_user.id
            print(f"✅ Demo user created (ID: {user_id})")

        # ── Team ──────────────────────────────────────────────────────────────
        existing_team = session.exec(
            select(Team).where(Team.name == "Anadolu Akademi")
        ).first()

        if existing_team:
            print(f"✅ Demo team already exists (ID: {existing_team.id})")
        else:
            demo_team = Team(
                name="Anadolu Akademi",
                age_group="U15",
                season="2025/2026",
                owner_id=user_id,
                primary_color="#10B981",
                secondary_color="#FFFFFF",
            )
            session.add(demo_team)
            session.commit()
            session.refresh(demo_team)
            print(f"✅ Demo team created (ID: {demo_team.id})")

    print("\n🎉 Setup complete!")
    print("   Login: dev@pitchvision.local / demo12345")


if __name__ == "__main__":
    setup_demo_data()
