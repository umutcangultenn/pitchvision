from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ReadBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class Identified(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ReadTimestampsOptional(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
