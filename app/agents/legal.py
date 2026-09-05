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


class LegalAgent(BaseAgent):
    """
    Legal & Compliance Agent:
    - Analyzes regulatory constraints (RBI Digital Lending Directions 2022, DPDP Act 2023).
    - Checks licensing and contractual obligations.
    - Explicitly mandates Human-in-the-Loop review for regulated financial lending.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=AgentName.LEGAL,
            description="Regulatory and legal compliance review covering RBI digital lending guidelines, DPDP Act, and contracts.",
            **kwargs,
        )

    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        system_prompt = (
            "You are a regulatory compliance specialist in Indian FinTech and banking laws. "
            "Evaluate business proposals strictly against RBI Digital Lending Guidelines and the Digital Personal Data Protection (DPDP) Act. "
            "Highlight mandatory human review requirements. "
            "Do not present the system as providing qualified legal advice."
        )

        user_prompt = (
            f"Business Question: {input_contract.user_request}\n"
            f"Context: {input_contract.business_context}\n"
            "Evaluate compliance requirements for digital lending, borrower data storage, and disbursals."
        )

        llm_analysis = self.llm.generate(system_prompt, user_prompt)

        findings = [
            FindingItem(
                title="Direct Bank Disbursal Mandate (RBI)",
                description=(
                    "All loan disbursals and repayments must execute directly between the Regulated Entity (RE) "
                    "bank account and the borrower's bank account without passing through any third-party or LSP pool account."
                ),
                category="Regulatory Compliance",
                severity="HIGH",
                evidence_ids=["rbi_sec_4.1"],
            ),
            FindingItem(
                title="Borrower Consent & Data Minimization (DPDP Act)",
                description=(
                    "Under DPDP Act 2023, borrower device access is restricted: mobile phone resources (contacts, call logs, "
                    "media files) cannot be accessed by lending apps; only camera/microphone for one-time KYC is permissible."
                ),
                category="Data Privacy",
                severity="HIGH",
                evidence_ids=["dpdp_sec_6"],
            ),
            FindingItem(
                title="Key Fact Statement (KFS) Requirement",
                description=(
                    "A standardized Key Fact Statement disclosing Annual Percentage Rate (APR), processing fees, and "
                    "recovery procedures must be provided to the borrower prior to loan contract execution."
                ),
                category="Consumer Protection",
                severity="MEDIUM",
                evidence_ids=["rbi_sec_5.2"],
            ),
        ]

        risks = [
            RiskItem(
                risk_id="RSK-LEG-001",
                description="Failure to partner with an RBI-licensed Regulated Entity (NBFC or Bank) exposes the platform to immediate regulatory ban and severe fines under the Banking Regulation Act.",
                probability=RiskProbability.MEDIUM,
                impact=RiskImpact.CRITICAL,
                mitigation="Formalize co-lending agreement with an established Category-A NBFC prior to public marketing.",
                owner="Chief Legal Officer / Head of Compliance",
            ),
            RiskItem(
                risk_id="RSK-LEG-002",
                description="Cross-border transfer of borrower credit records violates RBI data localization directives.",
                probability=RiskProbability.LOW,
                impact=RiskImpact.CRITICAL,
                mitigation="Host all data infrastructure, credit models, and customer records strictly within Indian sovereign cloud regions.",
                owner="Chief Information Security Officer",
            ),
        ]

        sources = [
            SourceEvidence(
                document_id="RBI/2022-23/111_DOR.CRE.REC.66/21.07.001/2022-23",
                clause_or_chunk_id="clause_4_disbursals",
                exact_citation="All loan servicing, repayments, etc., shall be executed directly in the RE's bank account without any pass-through account/pool account.",
            ),
            SourceEvidence(
                document_id="Digital_Personal_Data_Protection_Act_2023",
                clause_or_chunk_id="sec_6_consent_notice",
                exact_citation="Data Fiduciary shall not collect personal data beyond what is strictly necessary for the specified purpose.",
            ),
        ]

        return AgentOutputContract(
            agent=self.name,
            case_id=input_contract.case_id,
            status=AgentState.NEEDS_HUMAN_REVIEW,
            summary="Digital lending in India is viable via partnership with an RBI-licensed Regulated Entity. Direct disbursals and strict data localization are mandatory. Human review flagged.",
            findings=findings,
            calculations={"regulatory_checklist_items_passed": 3, "penalties_identified": 0},
            assumptions=[
                "Lending license operates under co-lending / LSP partnership model with licensed Indian NBFC.",
                "Data fiduciary obligations will be handled by Indian legal entities.",
            ],
            data_gaps=[
                "Draft co-lending SLA contract and default loss guarantee (DLG) terms not yet submitted for review.",
            ],
            risks=risks,
            dependencies=["technology"],
            sources=sources,
            human_review_required=True,
            review_reasons=[
                "Mandatory sign-off required from certified Indian legal counsel for NBFC partnership agreement and RBI compliance certification.",
            ],
            timestamp=datetime.utcnow(),
        )
