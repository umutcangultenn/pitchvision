from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


class Team(TimestampMixin, SQLModel, table=True):
    __tablename__ = "team"

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id", index=True)
    name: str = Field(max_length=255)
    age_category: str = Field(max_length=32, description="ör. U14")
    game_format: str = Field(max_length=32, description="ör. 11v11")
    default_formation: str = Field(max_length=32)
    pitch_length: float = Field(description="metre")
    pitch_width: float = Field(description="metre")
    season: str = Field(max_length=32)
