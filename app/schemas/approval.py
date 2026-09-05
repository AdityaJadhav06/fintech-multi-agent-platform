from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApprovalDecision(BaseModel):
    decision: str  # "APPROVED" or "REJECTED"
    comments: Optional[str] = ""


class ApprovalResponse(BaseModel):
    id: str
    case_id: str
    run_id: Optional[str]
    category: str
    reason: str
    decision: str
    reviewer_id: Optional[str]
    comments: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True
