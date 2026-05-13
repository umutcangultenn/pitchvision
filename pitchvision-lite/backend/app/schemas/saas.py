from pydantic import BaseModel, EmailStr, Field


class DemoRequestCreate(BaseModel):
    full_name: str = Field(max_length=255)
    club_name: str = Field(max_length=255)
    role: str = Field(max_length=64)
    email: EmailStr
    phone: str = Field(max_length=64)
    age_categories: str = Field(max_length=512, description="Virgülle ayrılmış yaş grupları")
    interest_module: str = Field(max_length=128)
    notes: str = Field(default="", max_length=4000)
    plan_interest: str | None = Field(default=None, max_length=64)
    intent: str | None = Field(default=None, max_length=32)


class DemoRequestResponse(BaseModel):
    status: str
    reference: str
