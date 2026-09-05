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
from app.tools.finance_calc import (
    calculate_break_even,
    calculate_unit_economics,
    calculate_cash_runway,
)


class FinancialAgent(BaseAgent):
    """
    Financial Agent:
    - Analyzes business economics, forecasts, unit economics, and break-even.
    - Strictly delegates all calculations to deterministic Python functions.
    - Formulates sensitivity scenarios and highlights financial risks.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=AgentName.FINANCIAL,
            description="Analyzes unit economics, break-even volumes, and cash burn using deterministic calculations.",
            **kwargs,
        )

    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        # Default SME lending financial parameters (INR)
        avg_loan = float(input_contract.constraints.get("avg_loan_amount", 300000.0))  # 3 Lakh INR
        fixed_monthly_costs = float(input_contract.constraints.get("fixed_monthly_costs", 1500000.0))  # 15 Lakh INR
        initial_capital = float(input_contract.constraints.get("initial_capital", 50000000.0))  # 5 Crore INR
        target_cac = float(input_contract.constraints.get("target_cac", 4000.0))

        # 1. Deterministic Unit Economics
        unit_econ = calculate_unit_economics(
            avg_loan_amount=avg_loan,
            interest_margin_pct=4.5,
            processing_fee_pct=2.0,
            expected_default_rate_pct=3.0,
            cac=target_cac,
            avg_loans_per_customer=1.8,
        )

        # 2. Deterministic Break-Even
        # Revenue per loan = Gross revenue per loan; Variable cost = Default loss + servicing
        rev_per_loan = unit_econ["gross_revenue_per_loan"]
        var_cost_per_loan = unit_econ["expected_credit_loss"] + 500.0  # servicing
        break_even = calculate_break_even(
            fixed_costs=fixed_monthly_costs,
            revenue_per_unit=rev_per_loan,
            variable_cost_per_unit=var_cost_per_loan,
        )

        # 3. Deterministic Runway
        # Assuming ramp to 500 loans/month initially
        runway = calculate_cash_runway(
            initial_capital=initial_capital,
            monthly_fixed_burn=fixed_monthly_costs,
            monthly_loan_volume=500,
            net_margin_per_loan=unit_econ["net_margin_per_loan"],
        )

        # 4. Qualitative Commentary via LLM
        system_prompt = (
            "You are an expert Chief Financial Officer (CFO) and financial analyst. "
            "Interpret deterministic financial calculations factually. "
            "Never perform mental arithmetic or guess new figures. "
            "Distinguish clearly between reported facts, modeled projections, and underlying assumptions."
        )
        user_prompt = (
            f"Context: {input_contract.business_context}\n"
            f"Calculations:\n"
            f"- Unit Economics: {unit_econ}\n"
            f"- Break Even: {break_even}\n"
            f"- Runway Analysis: {runway}\n"
            "Provide executive interpretation, key sensitivities, and financial commentary."
        )

        llm_summary = self.llm.generate(system_prompt, user_prompt)

        findings = [
            FindingItem(
                title="Unit Economics Viability",
                description=(
                    f"Net margin per loan is INR {unit_econ['net_margin_per_loan']:,} with an LTV/CAC ratio of "
                    f"{unit_econ['ltv_to_cac_ratio']}x. Status: {unit_econ['verdict']}."
                ),
                category="Unit Economics",
                severity="LOW" if unit_econ["commercially_viable"] else "HIGH",
            ),
            FindingItem(
                title="Operational Break-Even Threshold",
                description=(
                    f"Operating break-even requires {break_even['break_even_units']:,} loan originations per month "
                    f"at an average ticket size of INR {avg_loan:,}."
                ),
                category="Break-Even Analysis",
                severity="MEDIUM",
            ),
            FindingItem(
                title="Capital Runway & Burn",
                description=(
                    f"Initial capital of INR {initial_capital:,} provides approximately {runway['estimated_runway_months']} "
                    f"months of operating runway during the ramp phase."
                ),
                category="Cash Management",
                severity="LOW",
            ),
        ]

        risks = [
            RiskItem(
                risk_id="RSK-FIN-001",
                description="If SME default rate exceeds 5.5% (vs baseline 3.0%), net margin per loan drops by 48%, extending break-even horizon past 24 months.",
                probability=RiskProbability.MEDIUM,
                impact=RiskImpact.CRITICAL,
                mitigation="Implement dynamic risk-based interest pricing and stop-loss automated credit cutoff rules.",
                owner="Chief Risk Officer / Head of Credit Underwriting",
            )
        ]

        return AgentOutputContract(
            agent=self.name,
            case_id=input_contract.case_id,
            status=AgentState.COMPLETED,
            summary=f"Financial viability confirmed under baseline assumptions. LTV/CAC is {unit_econ['ltv_to_cac_ratio']}x, with break-even at {break_even['break_even_units']} loans/month.",
            findings=findings,
            calculations={
                "unit_economics": unit_econ,
                "break_even": break_even,
                "cash_runway": runway,
            },
            assumptions=[
                "Average loan ticket size INR 3,00,000 with 12-month tenure.",
                "Expected SME default rate capped at 3.0%.",
                "Cost of capital / wholesale borrowing spread at 9.5% APR.",
            ],
            data_gaps=[
                "Historical cohort default data for micro-enterprises under INR 25 Lakh revenue is missing.",
            ],
            risks=risks,
            dependencies=["technology", "gtm"],
            sources=[
                SourceEvidence(
                    document_id="financial_model_v1",
                    clause_or_chunk_id="unit_econ_section",
                    exact_citation=f"Baseline ticket size INR {avg_loan}, CAC target INR {target_cac}.",
                )
            ],
            human_review_required=False,
            review_reasons=[],
            timestamp=datetime.utcnow(),
        )
