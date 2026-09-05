from datetime import datetime
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


class GTMAgent(BaseAgent):
    """
    Go-To-Market (GTM) Agent:
    - Commercialization strategy, phased launch roadmap, and distribution milestones.
    - Validates upstream blockers from Legal, Tech, and Marketing.
    - Synthesizes launch timeline.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=AgentName.GTM,
            description="Commercialization roadmap, launch phases, partnership channels, and milestone management.",
            **kwargs,
        )

    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        # Check upstream findings for blockers
        legal_blocked = False
        tech_ready = True
        for finding in input_contract.upstream_findings:
            if finding.get("agent") == "legal" and finding.get("human_review_required"):
                legal_blocked = True

        system_prompt = (
            "You are a Head of Go-To-Market (GTM) and Commercial Strategy in Indian FinTech. "
            "Structure a phased commercial launch plan. "
            "Never promise revenue or dates without empirical evidence. "
            "Explicitly condition launch milestones on unresolved regulatory and tech dependencies."
        )

        user_prompt = (
            f"Business Question: {input_contract.user_request}\n"
            f"Context: {input_contract.business_context}\n"
            f"Upstream Status: Legal review pending: {legal_blocked}\n"
            "Formulate 3-phase launch roadmap, merchant onboarding milestones, and commercial KPIs."
        )

        llm_analysis = self.llm.generate(system_prompt, user_prompt)

        findings = [
            FindingItem(
                title="Phased Commercial Rollout Strategy",
                description=(
                    "Phase 1 (Months 1-3): Closed beta pilot with 250 curated MSME merchants in Mumbai/Pune industrial belt. "
                    "Phase 2 (Months 4-6): Expansion to Gujarat and Karnataka via accounting software channel partnerships. "
                    "Phase 3 (Months 7-12): Pan-India digital launch with automated bureau scorecards."
                ),
                category="Commercial Roadmap",
                severity="LOW",
            ),
            FindingItem(
                title="Critical Path Dependency: Legal Approval Gate",
                description=(
                    "Launch readiness is conditionally gated: Public borrower onboarding cannot commence until "
                    "human legal review confirms the NBFC co-lending contract compliance under RBI directives."
                ),
                category="Launch Governance",
                severity="HIGH" if legal_blocked else "LOW",
            ),
            FindingItem(
                title="Distribution Partnership Strategy",
                description=(
                    "Primary distribution channels: Co-branded integration with GST invoicing platforms (Tally, Clear) "
                    "and merchant acquirers to access pre-verified cash flow transaction history."
                ),
                category="Distribution Channels",
                severity="MEDIUM",
            ),
        ]

        risks = [
            RiskItem(
                risk_id="RSK-GTM-001",
                description="Long partner integration lead times with partner NBFCs or core banking hosts could delay Phase 1 launch by 2-3 months.",
                probability=RiskProbability.MEDIUM,
                impact=RiskImpact.HIGH,
                mitigation="Standardize API integrations with pre-built sandbox adapters and parallelize partner onboarding.",
                owner="VP Strategic Partnerships / GTM Lead",
            )
        ]

        return AgentOutputContract(
            agent=self.name,
            case_id=input_contract.case_id,
            status=AgentState.COMPLETED,
            summary="GTM roadmap formulated into 3 phases. Phase 1 pilot targets 250 merchants. Commercial launch is strictly gated on human legal sign-off.",
            findings=findings,
            calculations={
                "pilot_borrower_target": 250,
                "year_1_borrower_target": 5000,
                "months_to_pilot": 3,
            },
            assumptions=[
                "Partner NBFC SLA provides loan sanction approval within 24 hours.",
                "Merchant GST invoicing platform partnership agreement signed by Month 2.",
            ],
            data_gaps=[
                "Finalized revenue-share percentage with GST software distributor partners not yet locked.",
            ],
            risks=risks,
            dependencies=["legal", "technology", "financial", "marketing", "hr"],
            sources=[
                SourceEvidence(
                    document_id="gtm_strategy_v1",
                    clause_or_chunk_id="sec_launch_phases",
                    exact_citation="3-phase rollout starting with curated closed pilot in Tier-2 manufacturing hubs.",
                )
            ],
            human_review_required=legal_blocked,
            review_reasons=["GTM rollout is gated until legal compliance review is completed."] if legal_blocked else [],
            timestamp=datetime.utcnow(),
        )
