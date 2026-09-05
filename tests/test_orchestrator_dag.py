import pytest
from app.schemas.agent_contracts import AgentName
from app.orchestrator.planner import TaskGraphPlanner
from app.orchestrator.executor import OrchestratorExecutor
from app.orchestrator.synthesizer import ReportSynthesizer


def test_dag_planner_waves():
    planner = TaskGraphPlanner()
    waves = planner.build_execution_plan()

    assert len(waves) >= 3

    # Wave 1 must contain independent agents
    wave_1 = waves[0]
    assert AgentName.TECHNOLOGY in wave_1
    assert AgentName.FINANCIAL in wave_1
    assert AgentName.LEGAL in wave_1
    assert AgentName.MARKETING in wave_1
    assert AgentName.ESG in wave_1

    # HR depends on Technology, so HR cannot be in Wave 1
    assert AgentName.HR not in wave_1

    # Flatten waves to ensure all 8 agents are scheduled
    all_scheduled = [agent for wave in waves for agent in wave]
    assert len(all_scheduled) == 8


@pytest.mark.asyncio
async def test_full_orchestrator_execution():
    executor = OrchestratorExecutor()
    synthesizer = ReportSynthesizer()

    events_logged = []

    def callback(case_id, agent, state, msg):
        events_logged.append((agent.value, state.value))

    results = await executor.execute_case(
        case_id="CASE-DAG-TEST",
        org_id="ORG-TEST",
        user_request="Should we launch an AI-enabled lending product for SMEs in India?",
        business_context="FinTech startup evaluating working capital credit under RBI directives.",
        constraints={"target_cac": 4000, "initial_capital": 50000000},
        document_refs=[],
        event_callback=callback,
    )

    # Check all 8 agents executed
    assert len(results) == 8
    assert AgentName.FINANCIAL in results
    assert AgentName.LEGAL in results
    assert AgentName.TECHNOLOGY in results
    assert AgentName.HR in results
    assert AgentName.RISK in results

    # Verify Legal flagged human review required
    assert results[AgentName.LEGAL].human_review_required is True

    # Test Synthesis
    report = synthesizer.synthesize(
        case_id="CASE-DAG-TEST",
        master_question="Should we launch an AI-enabled lending product for SMEs in India?",
        agent_outputs=results,
    )

    assert report.case_id == "CASE-DAG-TEST"
    assert report.human_review_required is True
    assert len(report.central_risk_register) >= 5
    assert "financial" in report.deterministic_metrics
    assert len(report.key_findings) >= 10
