import pytest
from app.agents.hr import HRAgent
from app.schemas.agent_contracts import (
    AgentName,
    AgentInputContract,
    AgentOutputContract,
)
from app.tools.document_parser import cosine_similarity


def test_cosine_similarity_edge_cases():
    # Identical vectors
    v1 = [1.0, 0.0, 0.0]
    assert cosine_similarity(v1, v1) == 1.0

    # Orthogonal vectors
    v2 = [0.0, 1.0, 0.0]
    assert cosine_similarity(v1, v2) == 0.0

    # Opposite vectors
    v3 = [-1.0, 0.0, 0.0]
    assert cosine_similarity(v1, v3) == -1.0

    # Empty vectors
    assert cosine_similarity([], []) == 0.0


@pytest.mark.asyncio
async def test_hr_agent_execution_and_guardrails():
    hr_agent = HRAgent()

    input_contract = AgentInputContract(
        case_id="CASE-HR-TEST",
        org_id="ORG-TEST",
        user_request="Evaluate engineering talent for lending platform",
        business_context="FinTech credit underwriting startup in India",
        requested_task="Perform skill gap and resume ranking",
        constraints={
            "resumes": [
                {
                    "id": "CAND-01",
                    "filename": "expert_mlops.txt",
                    "resume_text": "MLOps Engineer with 5 years experience in Python, PyTorch, credit risk scoring, AWS ap-south-1.",
                },
                {
                    "id": "CAND-02",
                    "filename": "junior_frontend.txt",
                    "resume_text": "Frontend intern with 6 months HTML/CSS and WordPress experience.",
                },
            ]
        },
    )

    output = await hr_agent.run(input_contract)

    assert output.agent == AgentName.HR
    assert output.case_id == "CASE-HR-TEST"
    assert len(output.findings) >= 2
    assert len(output.risks) >= 1

    # Check that candidate ranking is present in calculations
    ranked = output.calculations.get("ranked_candidates", [])
    assert len(ranked) == 2
    # Ensure ranking has highest similarity first
    assert ranked[0]["similarity_score"] >= ranked[1]["similarity_score"]

    # Anti-bias verification: ensure prohibited keywords are absent in system outputs
    prohibited = ["gender", "religion", "race", "caste", "marital status", "age"]
    full_text = (output.summary + " " + " ".join(f.description for f in output.findings)).lower()
    for word in prohibited:
        assert f"is {word}" not in full_text
