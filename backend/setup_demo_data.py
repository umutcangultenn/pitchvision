"""
Setup demo data: user + team
Run: python setup_demo_data.py
"""
from sqlmodel import Session, create_engine, select
from app.models.user import User
from app.models.team import Team
from app.auth import get_password_hash
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def setup_demo_data():
    with Session(engine) as session:
        # 1. Create or get demo user
        existing_user = session.exec(select(User).where(User.email == "dev@pitchvision.local")).first()
        
        if existing_user:
            print(f"✅ Demo user exists (ID: {existing_user.id})")
            user_id = existing_user.id
        else:
            demo_user = User(
                email="dev@pitchvision.local",
                full_name="Development User",
                hashed_password="demo_hash",  # Simple hash for development
                is_active=True,
                role="coach"
            )
            session.add(demo_user)
            session.commit()
            session.refresh(demo_user)
            user_id = demo_user.id
            print(f"✅ Demo user created (ID: {user_id})")
        
        # 2. Create or get demo team
        existing_team = session.exec(select(Team).where(Team.name == "Anadolu Akademi")).first()
        
        if existing_team:
            print(f"✅ Demo team exists (ID: {existing_team.id})")
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
        
        print("\n🎉 Demo data ready!")
        print("   User: dev@pitchvision.local")
        print("   Team: Anadolu Akademi (U15)")

if __name__ == "__main__":
    setup_demo_data()
