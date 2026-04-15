"""Tests for benefits deduction module."""

from payroll.benefits import calculate_benefit_deductions


class TestBenefits:
    def test_no_elections(self):
        result = calculate_benefit_deductions({}, 5000.0)
        assert result["total"] == 0.0

    def test_health_basic(self):
        result = calculate_benefit_deductions({"health_basic": True}, 5000.0)
        assert result["deductions"]["health_basic"] == 125.0
        assert result["total"] == 125.0

    def test_401k_percentage(self):
        result = calculate_benefit_deductions({"401k": 0.06}, 5000.0)
        assert result["deductions"]["401k"] == 300.0  # 6% of 5000

    def test_multiple_benefits(self):
        elections = {
            "health_premium": True,
            "dental": True,
            "vision": True,
            "401k": 0.04,
        }
        result = calculate_benefit_deductions(elections, 4000.0)
        expected = 225.0 + 35.0 + 15.0 + 160.0  # 435
        assert result["total"] == expected

    def test_unknown_benefit_ignored(self):
        result = calculate_benefit_deductions({"nonexistent": True}, 5000.0)
        assert result["total"] == 0.0
