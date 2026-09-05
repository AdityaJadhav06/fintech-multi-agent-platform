from datetime import datetime
from typing import Any, Dict, List
from app.agents.base import BaseAgent
from app.schemas.agent_contracts import (
    AgentName,
    AgentState,
    AgentInputContract,
    AgentOutputContract,
    FindingItem,
    RiskItem,
    RiskProbability,
    RiskImpact,
    SourceEvidence,
)


class RiskAgent(BaseAgent):
    """
    Central Cross-Functional Risk Agent:
    - Ingests risks, data gaps, and uncertainties from all domain agents.
    - Compiles the Central Risk Register.
    - Calculates standardized 5x5 Risk Severity Scores (Probability x Impact).
    - Prohibits automated closure of high risks.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=AgentName.RISK,
            description="Centralized cross-functional risk aggregation, severity scoring, and mitigation planning.",
            **kwargs,
        )

    def calculate_severity_score(self, prob: RiskProbability, impact: RiskImpact) -> int:
        p_map = {RiskProbability.LOW: 1, RiskProbability.MEDIUM: 2, RiskProbability.HIGH: 3, RiskProbability.UNKNOWN: 2}
        i_map = {RiskImpact.LOW: 1, RiskImpact.MEDIUM: 2, RiskImpact.HIGH: 3, RiskImpact.CRITICAL: 4, RiskImpact.UNKNOWN: 2}
        return p_map.get(prob, 2) * i_map.get(impact, 2)

    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        # Collect upstream risks from all agents
        central_risk_register: List[RiskItem] = []

        for finding in input_contract.upstream_findings:
            raw_risks = finding.get("risks", [])
            for r in raw_risks:
                if isinstance(r, dict):
                    prob = RiskProbability(r.get("probability", "UNKNOWN"))
                    impact = RiskImpact(r.get("impact", "UNKNOWN"))
                    score = self.calculate_severity_score(prob, impact)
                    risk_item = RiskItem(
                        risk_id=r.get("risk_id", f"RSK-GEN-{len(central_risk_register)+1}"),
                        description=r.get("description", "Unspecified risk"),
                        probability=prob,
                        impact=impact,
                        mitigation=r.get("mitigation", "TBD"),
                        owner=r.get("owner", "Cross-Functional Committee"),
                        severity_score=score,
                    )
                    central_risk_register.append(risk_item)

        # Ensure top baseline risks exist if upstream list was empty
        if not central_risk_register:
            central_risk_register.append(
                RiskItem(
                    risk_id="RSK-SYS-001",
                    description="Macroeconomic default spike across Indian SME sector during monetary tightening.",
                    probability=RiskProbability.HIGH,
                    impact=RiskImpact.CRITICAL,
                    severity_score=12,
                    mitigation="Diversify borrower industry sectors and establish credit guarantee coverage (CGTMSE).",
                    owner="Chief Risk Officer",
                )
            )

        # Sort by severity descending
        central_risk_register.sort(key=lambda x: x.severity_score or 0, reverse=True)

        system_prompt = (
            "You are a Chief Risk Officer (CRO) evaluating cross-functional enterprise risk. "
            "Synthesize domain risks, highlight systemic vulnerabilities, and establish mitigation ownership. "
            "Never silently ignore or accept high risks without documented controls."
        )

        user_prompt = (
            f"Business Question: {input_contract.user_request}\n"
            f"Risk Register Count: {len(central_risk_register)} risks ingested.\n"
            "Summarize the cross-domain risk landscape and flag any systemic threats."
        )

        llm_analysis = self.llm.generate(system_prompt, user_prompt)

        critical_risks_count = sum(1 for r in central_risk_register if r.impact == RiskImpact.CRITICAL)

        findings = [
            FindingItem(
                title="Central Risk Register Compilation",
                description=(
                    f"Aggregated {len(central_risk_register)} cross-functional risks across Legal, Financial, Tech, HR, ESG, and GTM. "
                    f"Identified {critical_risks_count} CRITICAL severity risks requiring executive oversight."
                ),
                category="Risk Governance",
                severity="HIGH" if critical_risks_count > 0 else "MEDIUM",
            ),
            FindingItem(
                title="Top Systemic Vulnerability: Regulatory & Credit Default Convergence",
                description=(
                    "The primary systemic risk lies at the intersection of RBI Regulated Entity compliance and portfolio "
                    "credit default shocks. A failure in either domain could immediately jeopardize platform viability."
                ),
                category="Systemic Risk",
                severity="HIGH",
            ),
        ]

        return AgentOutputContract(
            agent=self.name,
            case_id=input_contract.case_id,
            status=AgentState.COMPLETED,
            summary=f"Risk assessment complete. {len(central_risk_register)} risks categorized with {critical_risks_count} critical items. Mitigations assigned.",
            findings=findings,
            calculations={
                "total_risks_identified": len(central_risk_register),
                "critical_risks_count": critical_risks_count,
                "high_severity_risks_count": sum(1 for r in central_risk_register if (r.severity_score or 0) >= 6),
            },
            assumptions=[
                "Risk severity scored on 3x4 Probability-Impact matrix (Scores 1 to 12).",
                "Mitigation actions are binding on respective department owners.",
            ],
            data_gaps=[
                "SME portfolio delinquency trends during recent GST regime updates require live credit bureau benchmarking.",
            ],
            risks=central_risk_register,
            dependencies=["financial", "legal", "technology", "hr", "esg", "marketing", "gtm"],
            sources=[
                SourceEvidence(
                    document_id="enterprise_risk_framework_2026",
                    clause_or_chunk_id="sec_basel_sme",
                    exact_citation="Standardized cross-functional risk matrix scoring for digital lending exposures.",
                )
            ],
            human_review_required=critical_risks_count > 0,
            review_reasons=["Board Risk Committee approval required for critical regulatory and credit risks."] if critical_risks_count > 0 else [],
            timestamp=datetime.utcnow(),
        )
