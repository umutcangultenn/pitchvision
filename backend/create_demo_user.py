"""
Create a demo user for testing.
Run: python create_demo_user.py
"""
from sqlmodel import Session, create_engine, select
from app.models.user import User
from app.auth import get_password_hash
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_demo_user():
    with Session(engine) as session:
        # Check if demo user exists
        existing = session.exec(select(User).where(User.email == "demo@pitchvision.com")).first()
        
        if existing:
            print("✅ Demo user already exists!")
            print(f"   Email: demo@pitchvision.com")
            print(f"   Password: demo123")
            return
        
        # Create demo user
        demo_user = User(
            email="demo@pitchvision.com",
            username="demo",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            is_active=True,
        )
        
        session.add(demo_user)
        session.commit()
        session.refresh(demo_user)
        
        print("✅ Demo user created successfully!")
        print(f"   Email: demo@pitchvision.com")
        print(f"   Password: demo123")
        print(f"   User ID: {demo_user.id}")

if __name__ == "__main__":
    create_demo_user()
