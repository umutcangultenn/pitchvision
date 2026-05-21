"""
Create a demo team for testing.
Run: python create_demo_team.py
"""
from sqlmodel import Session, create_engine, select
from app.models.team import Team
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_demo_team():
    with Session(engine) as session:
        # Check if demo team exists
        existing = session.exec(select(Team).where(Team.name == "Anadolu Akademi")).first()
        
        if existing:
            print("✅ Demo team already exists!")
            print(f"   Name: {existing.name}")
            print(f"   ID: {existing.id}")
            return
        
        # Create demo team
        demo_team = Team(
            name="Anadolu Akademi",
            age_group="U15",
            season="2025/2026",
            owner_id=1,  # Mock user ID
            coach_name="Demo Coach",
            home_color="Mavi",
            away_color="Beyaz",
        )
        
        session.add(demo_team)
        session.commit()
        session.refresh(demo_team)
        
        print("✅ Demo team created successfully!")
        print(f"   Name: {demo_team.name}")
        print(f"   ID: {demo_team.id}")
        print(f"   Age Group: {demo_team.age_group}")

if __name__ == "__main__":
    create_demo_team()
