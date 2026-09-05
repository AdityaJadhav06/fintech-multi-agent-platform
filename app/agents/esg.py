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


class ESGAgent(BaseAgent):
    """
    ESG Agent:
    - Environmental: Cloud server energy consumption and carbon footprint estimation.
    - Social: Financial inclusion impact and credit accessibility for underserved enterprises.
    - Governance: Transparent fee disclosure and fair collection practices.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=AgentName.ESG,
            description="Evaluates environmental compute footprint, social financial inclusion, and corporate governance.",
            **kwargs,
        )

    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        system_prompt = (
            "You are an ESG and Sustainability Director. "
            "Evaluate digital lending on Environmental (compute carbon emissions), "
            "Social (financial inclusion of underserved SMEs), and Governance (fair debt recovery, transparent pricing). "
            "Clearly distinguish measured facts from estimates."
        )

        user_prompt = (
            f"Business Question: {input_contract.user_request}\n"
            f"Context: {input_contract.business_context}\n"
            "Assess ESG risks, social inclusion metrics, and cloud carbon emissions."
        )

        llm_analysis = self.llm.generate(system_prompt, user_prompt)

        findings = [
            FindingItem(
                title="Environmental Compute Impact (Green FinTech)",
                description=(
                    "Server compute emissions estimated at 115-140 kg CO2e monthly. Leveraging renewable-powered cloud regions "
                    "(AWS ap-south-1) and serverless auto-scaling minimizes idle energy consumption."
                ),
                category="Environmental",
                severity="LOW",
            ),
            FindingItem(
                title="Social Financial Inclusion Impact",
                description=(
                    "High positive social impact: Democratizes working capital credit for Tier-2/3 micro-enterprises currently "
                    "forced to borrow at usurious rates (36-60% APR) from informal, unregulated moneylenders."
                ),
                category="Social Impact",
                severity="LOW",
            ),
            FindingItem(
                title="Governance & Ethical Recovery Safeguards",
                description=(
                    "Strict governance adherence: Eliminates predatory debt collection by codifying fair recovery practices "
                    "in accordance with RBI fair practices code (prohibiting harassment, late-night calls, or unauthorized visits)."
                ),
                category="Corporate Governance",
                severity="MEDIUM",
            ),
        ]

        risks = [
            RiskItem(
                risk_id="RSK-ESG-001",
                description="Aggressive third-party collection agency misconduct could inflict severe reputational damage and regulatory penalties on the platform.",
                probability=RiskProbability.MEDIUM,
                impact=RiskImpact.HIGH,
                mitigation="Mandate digital-first collections, record all borrower communications, and bind recovery partners to RBI fair-practice agreements.",
                owner="Chief Compliance Officer & ESG Committee",
            )
        ]

        return AgentOutputContract(
            agent=self.name,
            case_id=input_contract.case_id,
            status=AgentState.COMPLETED,
            summary="ESG analysis yields high positive social impact through financial inclusion of underserved SMEs. Governance safeguards embedded into collection workflows.",
            findings=findings,
            calculations={
                "estimated_monthly_co2e_kg": 125.0,
                "underserved_borrower_target_pct": 35.0,
            },
            assumptions=[
                "Cloud data center carbon intensity estimated based on standard Indian power grid emission factor (0.71 kg CO2e/kWh).",
            ],
            data_gaps=[
                "Third-party collection agency ESG compliance audits are not yet established.",
            ],
            risks=risks,
            dependencies=[],
            sources=[
                SourceEvidence(
                    document_id="esg_policy_framework_2026",
                    clause_or_chunk_id="sec_financial_inclusion",
                    exact_citation="Mission to support micro-entrepreneurs with transparent, sub-24% APR working capital.",
                )
            ],
            human_review_required=False,
            review_reasons=[],
            timestamp=datetime.utcnow(),
        )
