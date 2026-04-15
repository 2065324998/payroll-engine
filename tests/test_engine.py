"""Tests for the payroll engine."""

from datetime import date
import pytest
from payroll.engine import PayrollEngine
from payroll.employee import Employee, PayPeriod, ShiftHours


class TestPayrollEngine:
    def test_basic_paycheck(self):
        """Simple day-shift employee, no overtime, no benefits."""
        engine = PayrollEngine()
        employee = Employee(
            employee_id="E001",
            name="Alice Smith",
            base_hourly_rate=20.0,
        )
        period = PayPeriod(
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 14),
            shifts=[ShiftHours("day", regular_hours=80, overtime_hours=0)],
        )
        stub = engine.process(employee, period)
        assert stub.regular_pay == 1600.0
        assert stub.overtime_pay == 0.0
        assert stub.gross_pay == 1600.0
        assert stub.net_pay > 0

    def test_ytd_updates(self):
        """YTD totals should accumulate across pay periods."""
        engine = PayrollEngine()
        employee = Employee(
            employee_id="E002",
            name="Bob Jones",
            base_hourly_rate=25.0,
        )
        period1 = PayPeriod(
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 14),
            shifts=[ShiftHours("day", regular_hours=80, overtime_hours=0)],
        )
        stub1 = engine.process(employee, period1)
        assert stub1.ytd_gross == stub1.gross_pay

        period2 = PayPeriod(
            period_start=date(2024, 1, 15),
            period_end=date(2024, 1, 28),
            shifts=[ShiftHours("day", regular_hours=80, overtime_hours=0)],
        )
        stub2 = engine.process(employee, period2)
        assert stub2.ytd_gross == stub1.gross_pay + stub2.gross_pay

    def test_with_benefits(self):
        """Employee with health and 401k elections."""
        engine = PayrollEngine()
        employee = Employee(
            employee_id="E003",
            name="Carol Davis",
            base_hourly_rate=30.0,
            benefits_elections={"health_basic": True, "401k": 0.05},
        )
        period = PayPeriod(
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 14),
            shifts=[ShiftHours("day", regular_hours=80, overtime_hours=0)],
        )
        stub = engine.process(employee, period)
        # Health: 125.0, 401k: 2400 * 0.05 = 120.0
        assert stub.benefits_deductions == 245.0

    def test_with_bonus(self):
        """Bonus is included in gross pay and taxed."""
        engine = PayrollEngine()
        employee = Employee(
            employee_id="E004",
            name="Dave Wilson",
            base_hourly_rate=20.0,
        )
        period = PayPeriod(
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 14),
            shifts=[ShiftHours("day", regular_hours=80, overtime_hours=0)],
            bonus=500.0,
        )
        stub = engine.process(employee, period)
        assert stub.gross_pay == 2100.0  # 1600 + 500
        assert stub.bonus == 500.0

    def test_reimbursements_not_taxed(self):
        """Reimbursements add to net pay but don't affect gross or taxes."""
        engine = PayrollEngine()
        employee = Employee(
            employee_id="E005",
            name="Eve Brown",
            base_hourly_rate=20.0,
        )
        period_no_reimb = PayPeriod(
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 14),
            shifts=[ShiftHours("day", regular_hours=80, overtime_hours=0)],
        )
        period_with_reimb = PayPeriod(
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 14),
            shifts=[ShiftHours("day", regular_hours=80, overtime_hours=0)],
            reimbursements=200.0,
        )

        emp1 = Employee(employee_id="E005a", name="Eve1", base_hourly_rate=20.0)
        emp2 = Employee(employee_id="E005b", name="Eve2", base_hourly_rate=20.0)

        stub1 = engine.process(emp1, period_no_reimb)
        stub2 = engine.process(emp2, period_with_reimb)

        # Same gross and taxes
        assert stub1.gross_pay == stub2.gross_pay
        assert stub1.federal_tax == stub2.federal_tax
        # Net differs by reimbursement amount
        assert stub2.net_pay == pytest.approx(stub1.net_pay + 200.0, abs=0.01)
