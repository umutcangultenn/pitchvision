from typing import Optional

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin
from app.models.enums import ReportType


class Report(TimestampMixin, SQLModel, table=True):
    __tablename__ = "report"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: Optional[int] = Field(default=None, foreign_key="match.id", index=True)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id", index=True)

    report_type: ReportType = Field(
        sa_column=Column(
            SAEnum(
                ReportType,
                values_callable=lambda obj: [e.value for e in obj],
                native_enum=False,
                length=48,
            ),
            nullable=False,
        )
    )
    title: str = Field(max_length=255)
    summary: Optional[str] = Field(default=None)
    html_path: Optional[str] = Field(default=None, max_length=1024)
    pdf_path: Optional[str] = Field(default=None, max_length=1024)
