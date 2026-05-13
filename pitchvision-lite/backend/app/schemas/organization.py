from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import ReadBase


class OrganizationCreate(BaseModel):
    name: str = Field(max_length=255)
    city: str = Field(max_length=128)
    logo_url: Optional[str] = Field(default=None, max_length=1024)
    organization_type: str = Field(max_length=64)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=128)
    logo_url: Optional[str] = Field(default=None, max_length=1024)
    organization_type: Optional[str] = Field(default=None, max_length=64)


class OrganizationRead(ReadBase):
    name: str
    city: str
    logo_url: Optional[str]
    organization_type: str
