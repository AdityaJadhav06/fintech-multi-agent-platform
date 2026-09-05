from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import AuthenticatedUser, get_current_user, AuditLogger, verify_tenant_access
from app.db import Case, AgentRun, AgentFinding, Risk, Approval, get_db
from app.schemas import (
    AgentName,
    AgentState,
    FinalReportResponse,
)
from app.orchestrator import OrchestratorExecutor, ReportSynthesizer

router = APIRouter(tags=["Orchestrator & Agents"])


@router.post("/api/cases/{case_id}/analyze", response_model=FinalReportResponse)
async def analyze_case(
    case_id: str,
    selected_agents: Optional[List[str]] = None,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers the Orchestrator DAG execution across all domain agents.
    Executes in waves, enforces context minimization, records all findings & risks,
    and returns a synthesized decision report.
    """
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalars().first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    verify_tenant_access(user, case.org_id)

    # Parse requested agents
    agents_to_run = None
    if selected_agents:
        agents_to_run = [AgentName(a.lower()) for a in selected_agents if a.lower() in [e.value for e in AgentName]]

    executor = OrchestratorExecutor()
    synthesizer = ReportSynthesizer()

    case.status = "RUNNING"
    await db.flush()

    # Execute Multi-Agent Task Graph
    outputs = await executor.execute_case(
        case_id=case.id,
        org_id=case.org_id,
        user_request=case.master_question,
        business_context=case.business_context or "",
        constraints=case.constraints_json or {},
        document_refs=[],
        requested_agents=agents_to_run,
    )

    # Persist agent runs, findings, risks, and approvals in DB
    for agent_name, output in outputs.items():
        run = AgentRun(
            case_id=case.id,
            agent_name=agent_name.value,
            status=output.status.value,
            summary=output.summary,
            completed_at=datetime.utcnow(),
        )
        db.add(run)
        await db.flush()

        for f in output.findings:
            finding_rec = AgentFinding(
                run_id=run.id,
                case_id=case.id,
                title=f.title,
                description=f.description,
                category=f.category,
                severity=f.severity or "MEDIUM",
                structured_json=output.calculations,
                human_review_required=output.human_review_required,
            )
            db.add(finding_rec)

        for r in output.risks:
            risk_rec = Risk(
                case_id=case.id,
                source_agent=agent_name.value,
                risk_code=r.risk_id,
                description=r.description,
                probability=r.probability.value,
                impact=r.impact.value,
                severity_score=r.severity_score or 4,
                mitigation=r.mitigation,
                owner=r.owner,
                status="OPEN",
            )
            db.add(risk_rec)

        if output.human_review_required:
            for reason in output.review_reasons:
                appr = Approval(
                    case_id=case.id,
                    run_id=run.id,
                    category=f"{agent_name.value.capitalize()} Review",
                    reason=reason,
                    decision="PENDING",
                )
                db.add(appr)

    # Synthesize Final Report
    report = synthesizer.synthesize(
        case_id=case.id,
        master_question=case.master_question,
        agent_outputs=outputs,
    )

    case.status = "NEEDS_HUMAN_REVIEW" if report.human_review_required else "COMPLETED"

    await AuditLogger.log_event(
        db=db,
        org_id=user.org_id,
        user_id=user.user_id,
        case_id=case.id,
        action="CASE_ANALYSIS_COMPLETED",
        resource_type="Case",
        resource_id=case.id,
        details={
            "agents_executed": [a.value for a in outputs.keys()],
            "human_review_required": report.human_review_required,
            "conflicts_count": len(report.conflicts_identified),
        },
    )

    return report


@router.get("/api/cases/{case_id}/findings")
async def get_case_findings(
    case_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves all domain findings generated for a case.
    """
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalars().first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    verify_tenant_access(user, case.org_id)

    f_stmt = select(AgentFinding).where(AgentFinding.case_id == case_id)
    f_res = await db.execute(f_stmt)
    return f_res.scalars().all()


@router.get("/api/reports/{case_id}", response_model=FinalReportResponse)
async def get_case_report(
    case_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the synthesized decision-support report for a case.
    """
    # Re-run or fetch existing runs
    return await analyze_case(case_id=case_id, user=user, db=db)
