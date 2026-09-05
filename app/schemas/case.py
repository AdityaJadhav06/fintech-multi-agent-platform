from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    title: str
    master_question: str
    business_context: Optional[str] = ""
    constraints: Dict[str, Any] = Field(default_factory=dict)
    selected_agents: Optional[List[str]] = None


class CaseResponse(BaseModel):
    id: str
    org_id: str
    title: str
    master_question: str
    business_context: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    case_id: str
    filename: str
    file_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


class FinalReportResponse(BaseModel):
    case_id: str
    master_question: str
    synthesis_summary: str
    domain_summaries: Dict[str, str]
    key_findings: List[Dict[str, Any]]
    deterministic_metrics: Dict[str, Any]
    central_risk_register: List[Dict[str, Any]]
    open_questions_and_gaps: List[str]
    conflicts_identified: List[str]
    human_review_required: bool
    review_reasons: List[str]
    generated_at: datetime
