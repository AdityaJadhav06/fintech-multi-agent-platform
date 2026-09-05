from datetime import datetime
import pytest
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


def test_agent_input_contract_validation():
    contract = AgentInputContract(
        case_id="CASE-001",
        org_id="ORG-TEST",
        user_request="Launch AI lending in India",
        business_context="SME FinTech",
        requested_task="Perform Risk Review",
    )
    assert contract.case_id == "CASE-001"
    assert contract.org_id == "ORG-TEST"
    assert contract.document_refs == []
    assert contract.constraints == {}


def test_agent_output_contract_validation():
    output = AgentOutputContract(
        agent=AgentName.LEGAL,
        case_id="CASE-001",
        status=AgentState.NEEDS_HUMAN_REVIEW,
        summary="RBI compliance requires licensed NBFC partnership.",
        findings=[
            FindingItem(
                title="Direct Disbursal",
                description="Must disburse directly to borrower bank account.",
                category="Regulatory Compliance",
            )
        ],
        calculations={"items_checked": 5},
        assumptions=["Partner NBFC available"],
        data_gaps=[],
        risks=[
            RiskItem(
                risk_id="RSK-LEG-001",
                description="Unlicensed lending penalty.",
                probability=RiskProbability.MEDIUM,
                impact=RiskImpact.CRITICAL,
                mitigation="Partner with Category-A NBFC",
            )
        ],
        dependencies=["technology"],
        sources=[
            SourceEvidence(
                document_id="doc_rbi_guidelines",
                clause_or_chunk_id="chunk_4",
                exact_citation="Direct bank disbursal required.",
            )
        ],
        human_review_required=True,
        review_reasons=["Legal sign-off required."],
    )

    assert output.agent == AgentName.LEGAL
    assert output.human_review_required is True
    assert len(output.findings) == 1
    assert len(output.risks) == 1
    assert output.risks[0].probability == RiskProbability.MEDIUM
    assert output.risks[0].impact == RiskImpact.CRITICAL
