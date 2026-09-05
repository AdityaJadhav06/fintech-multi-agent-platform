import math
from typing import Any, Dict, List


def calculate_break_even(
    fixed_costs: float,
    revenue_per_unit: float,
    variable_cost_per_unit: float,
) -> Dict[str, Any]:
    """
    Deterministic Break-Even Calculation:
    Break-Even Volume = Fixed Costs / (Revenue per Unit - Variable Cost per Unit)
    """
    contribution_margin = revenue_per_unit - variable_cost_per_unit
    if contribution_margin <= 0:
        return {
            "break_even_units": -1,
            "contribution_margin_per_unit": round(contribution_margin, 2),
            "feasible": False,
            "notes": "Unit economics are negative; revenue per unit does not cover variable costs.",
        }

    units_needed = math.ceil(fixed_costs / contribution_margin)
    total_break_even_revenue = units_needed * revenue_per_unit

    return {
        "fixed_costs": fixed_costs,
        "revenue_per_unit": revenue_per_unit,
        "variable_cost_per_unit": variable_cost_per_unit,
        "contribution_margin_per_unit": round(contribution_margin, 2),
        "contribution_margin_ratio": round(contribution_margin / revenue_per_unit, 4),
        "break_even_units": units_needed,
        "break_even_revenue": round(total_break_even_revenue, 2),
        "feasible": True,
        "notes": f"Requires {units_needed:,} units per period to achieve operating break-even.",
    }


def calculate_unit_economics(
    avg_loan_amount: float,
    interest_margin_pct: float = 4.5,
    processing_fee_pct: float = 2.0,
    expected_default_rate_pct: float = 3.0,
    cac: float = 4000.0,
    avg_loans_per_customer: float = 1.8,
) -> Dict[str, Any]:
    """
    Deterministic Unit Economics for Digital Lending:
    Gross revenue per loan = Loan * (Interest Spread + Processing Fee)
    Credit Loss per loan = Loan * Default Rate
    Net Margin per loan = Gross Revenue - Credit Loss - Servicing Cost
    LTV = Net Margin * Loans per Customer
    LTV/CAC ratio determines commercial viability (benchmark >= 3.0x).
    """
    gross_revenue_per_loan = avg_loan_amount * ((interest_margin_pct + processing_fee_pct) / 100.0)
    expected_loss = avg_loan_amount * (expected_default_rate_pct / 100.0)
    servicing_cost_per_loan = 500.0  # standard digital servicing overhead (INR)

    net_margin_per_loan = gross_revenue_per_loan - expected_loss - servicing_cost_per_loan
    ltv = net_margin_per_loan * avg_loans_per_customer
    ltv_to_cac = round(ltv / cac, 2) if cac > 0 else 0.0

    is_viable = ltv_to_cac >= 3.0

    return {
        "avg_loan_amount": avg_loan_amount,
        "gross_revenue_per_loan": round(gross_revenue_per_loan, 2),
        "expected_credit_loss": round(expected_loss, 2),
        "net_margin_per_loan": round(net_margin_per_loan, 2),
        "customer_acquisition_cost": cac,
        "customer_lifetime_value": round(ltv, 2),
        "ltv_to_cac_ratio": ltv_to_cac,
        "commercially_viable": is_viable,
        "verdict": "STRONG" if ltv_to_cac >= 3.5 else ("ACCEPTABLE" if is_viable else "UNVIABLE"),
    }


def calculate_cash_runway(
    initial_capital: float,
    monthly_fixed_burn: float,
    monthly_loan_volume: int,
    net_margin_per_loan: float,
    months_projected: int = 18,
) -> Dict[str, Any]:
    """
    Projects monthly cash burn and runway in months.
    """
    monthly_net_cash_flow = (monthly_loan_volume * net_margin_per_loan) - monthly_fixed_burn

    if monthly_net_cash_flow >= 0:
        runway_months = 999  # Self-sustaining / Cash flow positive
    else:
        runway_months = round(initial_capital / abs(monthly_net_cash_flow), 1)

    return {
        "initial_capital": initial_capital,
        "monthly_fixed_burn": monthly_fixed_burn,
        "monthly_net_cash_flow": round(monthly_net_cash_flow, 2),
        "estimated_runway_months": runway_months,
        "is_cash_flow_positive": monthly_net_cash_flow >= 0,
    }


def calculate_loan_amortization(
    principal: float,
    annual_rate_pct: float,
    tenure_months: int,
) -> Dict[str, Any]:
    """
    Standard monthly Equated Monthly Installment (EMI):
    EMI = [P * r * (1 + r)^n] / [(1 + r)^n - 1]
    """
    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        factor = math.pow(1 + monthly_rate, tenure_months)
        emi = (principal * monthly_rate * factor) / (factor - 1)

    total_payment = emi * tenure_months
    total_interest = total_payment - principal

    return {
        "principal": principal,
        "annual_interest_rate_pct": annual_rate_pct,
        "tenure_months": tenure_months,
        "monthly_emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
    }
