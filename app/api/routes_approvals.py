from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import AuthenticatedUser, get_current_user, AuditLogger
from app.db import Approval, get_db
from app.schemas import ApprovalDecision, ApprovalResponse

router = APIRouter(prefix="/api/approvals", tags=["Human Approvals"])


@router.get("", response_model=List[ApprovalResponse])
async def list_approvals(
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists all pending Human-in-the-Loop review requests.
    """
    stmt = select(Approval).order_by(Approval.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
async def submit_approval_decision(
    approval_id: str,
    payload: ApprovalDecision,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Records an authorized human review decision (APPROVED or REJECTED) with comments.
    """
    stmt = select(Approval).where(Approval.id == approval_id)
    result = await db.execute(stmt)
    approval = result.scalars().first()

    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    decision_norm = payload.decision.upper()
    if decision_norm not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=400, detail="Decision must be 'APPROVED' or 'REJECTED'.")

    approval.decision = decision_norm
    approval.reviewer_id = user.user_id
    approval.comments = payload.comments or ""
    approval.reviewed_at = datetime.utcnow()

    await AuditLogger.log_event(
        db=db,
        org_id=user.org_id,
        user_id=user.user_id,
        case_id=approval.case_id,
        action=f"APPROVAL_{decision_norm}",
        resource_type="Approval",
        resource_id=approval.id,
        details={"decision": decision_norm, "comments": payload.comments},
    )

    return approval
