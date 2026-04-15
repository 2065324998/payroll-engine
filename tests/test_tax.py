"""Tests for tax calculation module."""

import pytest
from payroll.tax import (
    get_tax_rate, calculate_marginal_tax, calculate_tax,
    TAX_BRACKETS, SOCIAL_SECURITY_RATE, MEDICARE_RATE,
)


class TestTaxRates:
    def test_lowest_bracket(self):
        assert get_tax_rate(5000) == 0.10

    def test_second_bracket(self):
        assert get_tax_rate(30000) == 0.12

    def test_third_bracket(self):
        assert get_tax_rate(60000) == 0.22

    def test_bracket_structure(self):
        """Brackets should be contiguous and ascending."""
        for i in range(len(TAX_BRACKETS) - 1):
            assert TAX_BRACKETS[i][1] == TAX_BRACKETS[i + 1][0]


class TestTaxCalculation:
    def test_tax_within_first_bracket(self):
        """Income fully within bracket 1 — flat and marginal rates agree."""
        tax = calculate_marginal_tax(10000)
        # 10000 * 0.10 = 1000 (same for flat or marginal within one bracket)
        assert tax == 1000.0

    def test_payroll_tax_basic(self):
        """Basic payroll tax calculation."""
        result = calculate_tax(2000, pay_periods_per_year=26)
        assert "federal_tax" in result
        assert "social_security" in result
        assert "medicare" in result
        assert result["social_security"] == round(2000 * SOCIAL_SECURITY_RATE, 2)
        assert result["medicare"] == round(2000 * MEDICARE_RATE, 2)

    def test_social_security_wage_base(self):
        """Social Security stops at wage base."""
        # YTD already at wage base — no more SS tax
        result = calculate_tax(5000, ytd_gross=170000)
        assert result["social_security"] == 0.0

    def test_medicare_always_applies(self):
        """Medicare has no wage base limit."""
        result = calculate_tax(5000, ytd_gross=500000)
        assert result["medicare"] > 0
