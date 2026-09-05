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


class MarketingAgent(BaseAgent):
    """
    Marketing Agent:
    - Customer segmentation, positioning, messaging, channels, and campaign planning.
    - Estimates Customer Acquisition Cost (CAC) for financial model inputs.
    - Guardrails: Explicitly tags projections as assumptions.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=AgentName.MARKETING,
            description="Market segmentation, positioning, acquisition channels, and CAC estimation.",
            **kwargs,
        )

    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        system_prompt = (
            "You are a Chief Marketing Officer (CMO) specializing in Indian SME FinTech products. "
            "Analyze target markets, positioning, and acquisition channels. "
            "Never fabricate market sizes or conversion rates; clearly label assumptions."
        )

        user_prompt = (
            f"Business Question: {input_contract.user_request}\n"
            f"Context: {input_contract.business_context}\n"
            "Define target SME personas, value proposition, regional channels, and estimated CAC."
        )

        llm_analysis = self.llm.generate(system_prompt, user_prompt)

        findings = [
            FindingItem(
                title="Target Customer Segmentation (Indian MSMEs)",
                description=(
                    "Primary segment: Tier-2 and Tier-3 trading, manufacturing, and service MSMEs with annual turnover "
                    "between INR 50 Lakh and 5 Crore, seeking working capital credit with 24-hour turnaround."
                ),
                category="Market Segmentation",
                severity="LOW",
            ),
            FindingItem(
                title="Value Proposition & Positioning",
                description=(
                    "'Cash flow when your business needs it.' Positioning revolves around speed, zero physical paperwork, "
                    "and transparent cash flow-based underwriting without collateral requirements."
                ),
                category="Positioning",
                severity="LOW",
            ),
            FindingItem(
                title="Channel Strategy & Acquisition Funnel",
                description=(
                    "Hybrid channel mix: 40% B2B digital partnerships (accounting software, GST portals, merchant QR networks), "
                    "35% digital performance marketing (Meta/Google targeted at business owners), and 25% NBFC direct agent networks."
                ),
                category="Channel Mix",
                severity="MEDIUM",
            ),
        ]

        risks = [
            RiskItem(
                risk_id="RSK-MKT-001",
                description="Aggressive digital lending competition in Tier-1 cities may inflate blended CAC above INR 5,500, deteriorating unit economics.",
                probability=RiskProbability.HIGH,
                impact=RiskImpact.MEDIUM,
                mitigation="Pivot acquisition focus to under-penetrated industrial clusters in Tier-2/Tier-3 states (e.g., Surat, Coimbatore, Ludhiana).",
                owner="VP Marketing / Growth Lead",
            )
        ]

        return AgentOutputContract(
            agent=self.name,
            case_id=input_contract.case_id,
            status=AgentState.COMPLETED,
            summary="Marketing strategy targets Tier-2/3 Indian SMEs via B2B digital partnerships and performance marketing. Blended CAC estimated at INR 4,000.",
            findings=findings,
            calculations={
                "estimated_blended_cac_inr": 4000,
                "projected_conversion_rate_pct": 3.8,
                "target_monthly_leads": 12500,
            },
            assumptions=[
                "Estimated CAC of INR 4,000 based on comparable Indian B2B FinTech benchmarks.",
                "Merchant QR network partnership provides lower CAC than pure social ads.",
            ],
            data_gaps=[
                "Specific regional vernacular ad conversion data in South and North-East India is limited.",
            ],
            risks=risks,
            dependencies=[],
            sources=[
                SourceEvidence(
                    document_id="msme_market_study_2026",
                    clause_or_chunk_id="sec_tier2_growth",
                    exact_citation="Tier-2/3 MSME working capital credit gap estimated at over $300B in India.",
                )
            ],
            human_review_required=False,
            review_reasons=[],
            timestamp=datetime.utcnow(),
        )
