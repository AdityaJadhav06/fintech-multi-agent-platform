import pytest
from app.tools.finance_calc import (
    calculate_break_even,
    calculate_unit_economics,
    calculate_cash_runway,
    calculate_loan_amortization,
)


def test_break_even_calculation_positive():
    # Fixed costs: 15,00,000 INR
    # Revenue per loan: 19,500 INR
    # Variable cost per loan: 9,500 INR (credit loss + servicing)
    # Contribution margin: 10,000 INR -> Units needed: 150
    result = calculate_break_even(
        fixed_costs=1500000.0,
        revenue_per_unit=19500.0,
        variable_cost_per_unit=9500.0,
    )
    assert result["feasible"] is True
    assert result["contribution_margin_per_unit"] == 10000.0
    assert result["break_even_units"] == 150
    assert result["break_even_revenue"] == 150 * 19500.0


def test_break_even_calculation_negative():
    result = calculate_break_even(
        fixed_costs=100000.0,
        revenue_per_unit=500.0,
        variable_cost_per_unit=600.0,
    )
    assert result["feasible"] is False
    assert result["break_even_units"] == -1


def test_unit_economics_positive():
    result = calculate_unit_economics(
        avg_loan_amount=300000.0,
        interest_margin_pct=4.5,
        processing_fee_pct=2.0,
        expected_default_rate_pct=3.0,
        cac=4000.0,
        avg_loans_per_customer=1.8,
    )
    # Gross rev = 300,000 * 6.5% = 19,500
    assert result["gross_revenue_per_loan"] == 19500.0
    # Expected loss = 300,000 * 3.0% = 9,000
    assert result["expected_credit_loss"] == 9000.0
    # Net margin = 19,500 - 9,000 - 500 = 10,000
    assert result["net_margin_per_loan"] == 10000.0
    # LTV = 10,000 * 1.8 = 18,000
    assert result["customer_lifetime_value"] == 18000.0
    # LTV/CAC = 18,000 / 4,000 = 4.5
    assert result["ltv_to_cac_ratio"] == 4.5
    assert result["commercially_viable"] is True
    assert result["verdict"] == "STRONG"


def test_cash_runway_positive_flow():
    # When net cash flow is positive
    result = calculate_cash_runway(
        initial_capital=50000000.0,
        monthly_fixed_burn=1000000.0,
        monthly_loan_volume=200,
        net_margin_per_loan=10000.0,
    )
    assert result["is_cash_flow_positive"] is True
    assert result["estimated_runway_months"] == 999


def test_loan_amortization():
    result = calculate_loan_amortization(
        principal=100000.0,
        annual_rate_pct=12.0,
        tenure_months=12,
    )
    assert result["principal"] == 100000.0
    assert result["tenure_months"] == 12
    assert result["monthly_emi"] > 8800.0
    assert result["total_interest"] > 0
