from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentName(str, Enum):
    MARKETING = "marketing"
    FINANCIAL = "financial"
    LEGAL = "legal"
    TECHNOLOGY = "technology"
    HR = "hr"
    ESG = "esg"
    GTM = "gtm"
    RISK = "risk"
    ORCHESTRATOR = "orchestrator"


class AgentState(str, Enum):
    PENDING = "PENDING"
    WAITING_FOR_DEPENDENCY = "WAITING_FOR_DEPENDENCY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
    SKIPPED = "SKIPPED"


class RiskProbability(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class RiskImpact(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class RiskItem(BaseModel):
    risk_id: str
    description: str
    probability: RiskProbability = RiskProbability.UNKNOWN
    impact: RiskImpact = RiskImpact.UNKNOWN
    mitigation: str
    owner: Optional[str] = None
    severity_score: Optional[int] = None  # 1 to 25 score calculated by Risk matrix


class SourceEvidence(BaseModel):
    document_id: str
    clause_or_chunk_id: str
    exact_citation: str
    confidence_score: Optional[float] = None


class FindingItem(BaseModel):
    title: str
    description: str
    category: str
    severity: Optional[str] = "MEDIUM"
    evidence_ids: List[str] = Field(default_factory=list)


class AgentInputContract(BaseModel):
    case_id: str
    org_id: str
    user_request: str
    business_context: str
    document_refs: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    requested_task: str
    upstream_findings: List[Dict[str, Any]] = Field(default_factory=list)


class AgentOutputContract(BaseModel):
    agent: AgentName
    case_id: str
    status: AgentState
    summary: str
    findings: List[FindingItem] = Field(default_factory=list)
    calculations: Dict[str, Any] = Field(default_factory=dict)
    assumptions: List[str] = Field(default_factory=list)
    data_gaps: List[str] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    sources: List[SourceEvidence] = Field(default_factory=list)
    human_review_required: bool = False
    review_reasons: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
