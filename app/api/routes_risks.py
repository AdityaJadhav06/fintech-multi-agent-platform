from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import AuthenticatedUser, get_current_user, verify_tenant_access
from app.db import Case, Risk, get_db
from app.schemas import RiskRecord

router = APIRouter(prefix="/api/cases/{case_id}/risks", tags=["Risk Register"])


@router.get("", response_model=List[RiskRecord])
async def get_case_risks(
    case_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the Central Risk Register compiled across all domain agents.
    """
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalars().first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    verify_tenant_access(user, case.org_id)

    r_stmt = select(Risk).where(Risk.case_id == case_id).order_by(Risk.severity_score.desc())
    r_res = await db.execute(r_stmt)
    return r_res.scalars().all()
