"""
Interactive Console Demonstration of the FinTech Multi-Agent Platform.
Executes the master business scenario:
"Should we launch an AI-enabled lending product for SMEs in India?"
Demonstrates:
- 4-Wave DAG Orchestrator
- Parallel Wave Concurrency
- Deterministic Math Tools
- Anti-Bias HR Candidate Ranking
- Central Risk Register Compilation
- Conflict Detection & Human Review Flags
"""

import asyncio
from app.db import init_db
from app.schemas.agent_contracts import AgentName
from app.orchestrator.executor import OrchestratorExecutor
from app.orchestrator.synthesizer import ReportSynthesizer


def print_banner(title: str):
    print("\n" + "=" * 75)
    print(f"  {title.center(71)}")
    print("=" * 75 + "\n")


async def run_demo():
    print_banner("FINTECH MULTI-AGENT DECISION-SUPPORT PLATFORM")
    print("Master Scenario: 'Should we launch an AI-enabled lending product for SMEs in India?'")
    print("Initializing Database & Seed Entities...")
    await init_db()

    executor = OrchestratorExecutor()
    synthesizer = ReportSynthesizer()

    def live_event_callback(case_id, agent, state, message):
        print(f"  [ORCHESTRATOR EVENT] [{agent.value.upper():<12}] -> State: {state.value:<10} | {message}")

    print("\nExecuting 4-Wave Multi-Agent Task Graph:")
    print("-" * 75)

    outputs = await executor.execute_case(
        case_id="CASE-DEMO-IND-001",
        org_id="ORG-DEFAULT-001",
        user_request="Should we launch an AI-enabled lending product for SMEs in India?",
        business_context="FinTech startup exploring working capital credit under RBI directives.",
        constraints={
            "initial_capital": 50000000.0,
            "avg_loan_amount": 300000.0,
            "target_cac": 4000.0,
        },
        document_refs=[],
        event_callback=live_event_callback,
    )

    print("-" * 75)
    print("\nAll 8 Domain Agents completed analysis successfully.")

    # Synthesize Final Report
    report = synthesizer.synthesize(
        case_id="CASE-DEMO-IND-001",
        master_question="Should we launch an AI-enabled lending product for SMEs in India?",
        agent_outputs=outputs,
    )

    # Display Key Highlights
    print_banner("DETERMINISTIC FINANCIAL METRICS (Python Tools)")
    fin_metrics = report.deterministic_metrics.get("financial", {})
    if "unit_economics" in fin_metrics:
        ue = fin_metrics["unit_economics"]
        print(f"  * Average Loan Size:     INR {ue['avg_loan_amount']:,.2f}")
        print(f"  * Gross Revenue / Loan:  INR {ue['gross_revenue_per_loan']:,.2f}")
        print(f"  * Expected Loss / Loan:  INR {ue['expected_credit_loss']:,.2f}")
        print(f"  * Net Margin / Loan:     INR {ue['net_margin_per_loan']:,.2f}")
        print(f"  * LTV / CAC Ratio:       {ue['ltv_to_cac_ratio']}x ({ue['verdict']})")

    if "break_even" in fin_metrics:
        be = fin_metrics["break_even"]
        print(f"  * Break-Even Volume:     {be['break_even_units']:,} loans / month")

    print_banner("CENTRAL RISK REGISTER (Severity Matrix P x I)")
    print(f"  {'Risk Code':<14} {'Agent':<12} {'Severity':<10} {'Impact':<10} {'Description'}")
    print("  " + "-" * 71)
    for risk in report.central_risk_register[:5]:
        sev = str(risk.get("severity_score") if risk.get("severity_score") is not None else "N/A")
        print(f"  {risk['risk_id']:<14} {risk['agent']:<12} {sev:<10} {risk['impact']:<10} {risk['description'][:40]}...")

    print_banner("GOVERNANCE & HUMAN REVIEW GATES")
    print(f"  * Human Review Required: {report.human_review_required}")
    for reason in report.review_reasons:
        print(f"    - [GATE TRIGGERED]: {reason}")

    if report.conflicts_identified:
        print("\n  * Cross-Domain Conflicts Reconciled:")
        for c in report.conflicts_identified:
            print(f"    - {c}")

    print_banner("EXECUTIVE BRIEFING SUMMARY")
    print(report.synthesis_summary.strip())
    print("\n" + "=" * 75 + "\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
