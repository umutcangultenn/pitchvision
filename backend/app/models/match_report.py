from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class MatchReportBase(SQLModel):
    """Base match report data"""
    match_summary: str  # AI-generated summary
    key_findings: str = Field(default="")  # JSON string of findings
    team_shape_metrics: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    tactical_recommendations: str = Field(default="")  # JSON string of recommendations
    next_match_focus: str = Field(default="")  # JSON string of focus areas
    report_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class MatchReport(MatchReportBase, table=True):
    __tablename__ = "match_reports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="matches.id")
    status: ReportStatus = ReportStatus.PENDING
    generated_by: str = "ai_nvidia"  # Which AI generated this
    generated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    match: "Match" = Relationship(back_populates="match_report")


class MatchReportCreate(MatchReportBase):
    match_id: int


class MatchReportRead(MatchReportBase):
    id: int
    match_id: int
    status: ReportStatus
    generated_by: str
    generated_at: Optional[datetime]
    created_at: datetime
    disclaimer: str = "Bu rapor otomatik analiz adayıdır. Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır."
    
    @property
    def key_findings_list(self) -> list[str]:
        """Parse key_findings JSON string to list"""
        import json
        try:
            return json.loads(self.key_findings) if self.key_findings else []
        except:
            return []
    
    @property
    def tactical_recommendations_list(self) -> list[str]:
        """Parse tactical_recommendations JSON string to list"""
        import json
        try:
            return json.loads(self.tactical_recommendations) if self.tactical_recommendations else []
        except:
            return []
    
    @property
    def next_match_focus_list(self) -> list[str]:
        """Parse next_match_focus JSON string to list"""
        import json
        try:
            return json.loads(self.next_match_focus) if self.next_match_focus else []
        except:
            return []
