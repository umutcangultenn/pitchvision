from typing import Optional

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin
from app.models.enums import UserRole


class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=320)
    full_name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    role: UserRole = Field(
        sa_column=Column(
            SAEnum(
                UserRole,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=32,
            ),
            nullable=False,
        )
    )
    organization_id: int = Field(foreign_key="organization.id", index=True)
    is_active: bool = Field(default=True)
