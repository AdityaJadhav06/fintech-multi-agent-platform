from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.agent_contracts import RiskProbability, RiskImpact


class RiskRecord(BaseModel):
    id: str
    case_id: str
    source_agent: str
    description: str
    probability: RiskProbability
    impact: RiskImpact
    severity_score: int
    mitigation: str
    owner: Optional[str] = None
    status: str = "OPEN"
    created_at: datetime

    class Config:
        from_attributes = True
