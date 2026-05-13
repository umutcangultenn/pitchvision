from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import ReportType
from app.schemas.base import ReadBase


class ReportCreate(BaseModel):
    match_id: Optional[int] = None
    player_id: Optional[int] = None
    report_type: ReportType
    title: str = Field(max_length=255)
    summary: Optional[str] = None
    html_path: Optional[str] = Field(default=None, max_length=1024)
    pdf_path: Optional[str] = Field(default=None, max_length=1024)


class ReportUpdate(BaseModel):
    match_id: Optional[int] = None
    player_id: Optional[int] = None
    report_type: Optional[ReportType] = None
    title: Optional[str] = Field(default=None, max_length=255)
    summary: Optional[str] = None
    html_path: Optional[str] = Field(default=None, max_length=1024)
    pdf_path: Optional[str] = Field(default=None, max_length=1024)


class ReportRead(ReadBase):
    match_id: Optional[int]
    player_id: Optional[int]
    report_type: ReportType
    title: str
    summary: Optional[str]
    html_path: Optional[str]
    pdf_path: Optional[str]
