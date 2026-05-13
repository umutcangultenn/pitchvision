from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole
from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.COACH
    organization_id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
