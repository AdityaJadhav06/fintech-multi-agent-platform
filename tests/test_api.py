import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db import init_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    await init_db()


@pytest.mark.asyncio
async def test_root_and_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "FinTech Multi-Agent Platform"
        assert len(data["agents"]) == 9

        health_resp = await ac.get("/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_case_lifecycle_and_orchestration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create Case
        create_payload = {
            "title": "India SME Lending Evaluation",
            "master_question": "Should we launch an AI-enabled lending product for SMEs in India?",
            "business_context": "Exploring digital micro-lending under RBI guidelines.",
            "constraints": {"target_cac": 4000, "initial_capital": 50000000},
        }
        case_resp = await ac.post("/api/cases", json=create_payload)
        assert case_resp.status_code == 201
        case_data = case_resp.json()
        case_id = case_data["id"]
        assert case_data["title"] == "India SME Lending Evaluation"

        # 2. Upload Document
        files = {"file": ("rbi_guidelines.txt", b"All loan disbursals must flow directly from bank accounts.", "text/plain")}
        doc_resp = await ac.post(f"/api/cases/{case_id}/documents", files=files)
        assert doc_resp.status_code == 201
        doc_data = doc_resp.json()
        assert doc_data["filename"] == "rbi_guidelines.txt"

        # 3. Trigger Orchestrated Multi-Agent Analysis
        analyze_resp = await ac.post(f"/api/cases/{case_id}/analyze")
        assert analyze_resp.status_code == 200
        report = analyze_resp.json()
        assert report["case_id"] == case_id
        assert len(report["domain_summaries"]) == 8
        assert report["human_review_required"] is True

        # 4. Check Risk Register
        risks_resp = await ac.get(f"/api/cases/{case_id}/risks")
        assert risks_resp.status_code == 200
        risks = risks_resp.json()
        assert len(risks) >= 5

        # 5. Check Human Review Approvals
        approvals_resp = await ac.get("/api/approvals")
        assert approvals_resp.status_code == 200
        approvals = approvals_resp.json()
        assert len(approvals) >= 1

        # 6. Submit Approval Decision
        appr_id = approvals[0]["id"]
        decision_resp = await ac.post(
            f"/api/approvals/{appr_id}/decision",
            json={"decision": "APPROVED", "comments": "Partner NBFC licensed under RBI approved."},
        )
        assert decision_resp.status_code == 200
        assert decision_resp.json()["decision"] == "APPROVED"
