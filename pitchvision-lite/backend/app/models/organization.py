from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


class Organization(TimestampMixin, SQLModel, table=True):
    __tablename__ = "organization"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    city: str = Field(max_length=128)
    logo_url: Optional[str] = Field(default=None, max_length=1024)
    organization_type: str = Field(max_length=64, description="ör. academy, club, school")
