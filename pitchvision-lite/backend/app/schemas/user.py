from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole
from app.schemas.base import ReadBase


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128, description="düz metin; API katmanında hash'lenir")
    role: UserRole
    organization_id: int
    is_active: bool = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    role: Optional[UserRole] = None
    organization_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserRead(ReadBase):
    email: str
    full_name: str
    role: UserRole
    organization_id: int
    is_active: bool
