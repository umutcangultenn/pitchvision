from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List, Any
from datetime import datetime


class ScoutNoteBase(SQLModel):
    player_id: int = Field(foreign_key="players.id", index=True)
    note: str
    rating: Optional[float] = None          # 0-10
    tags_json: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))


class ScoutNote(ScoutNoteBase, table=True):
    __tablename__ = "scout_notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    scout_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ScoutNoteCreate(ScoutNoteBase):
    pass


class ScoutNoteRead(ScoutNoteBase):
    id: int
    scout_id: int
    created_at: datetime
