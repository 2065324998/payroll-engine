"""Payroll processing engine."""

from payroll.employee import Employee, PayPeriod, PayStub
from payroll.tax import calculate_tax
from payroll.overtime import calculate_overtime_pay
from payroll.benefits import calculate_benefit_deductions


class PayrollEngine:
    """Processes payroll for employees, generating pay stubs.

    Handles the full payroll calculation pipeline:
    1. Calculate regular pay with shift differentials
    2. Calculate overtime pay
    3. Add bonuses, commissions, reimbursements
    4. Calculate tax withholdings
    5. Calculate benefit deductions
    6. Produce final pay stub with net pay
    """

    def __init__(self, pay_periods_per_year: int = 26):
        self.pay_periods_per_year = pay_periods_per_year

    def process(self, employee: Employee,
                pay_period: PayPeriod) -> PayStub:
        """Process payroll for a single employee and pay period."""

        # Step 1: Calculate earnings
        earnings = calculate_overtime_pay(
            pay_period.shifts, employee.base_hourly_rate
        )

        regular_pay = earnings["regular_pay"]
        overtime_pay = earnings["overtime_pay"]
        shift_diff_pay = earnings["shift_differential_pay"]

        # Step 2: Add supplemental income
        bonus = pay_period.bonus
        commission = pay_period.commission

        # Gross pay (excluding reimbursements — they're not taxable)
        gross_pay = (regular_pay + overtime_pay + shift_diff_pay +
                     bonus + commission)

        # Step 3: Calculate taxes
        taxes = calculate_tax(
            gross_pay,
            self.pay_periods_per_year,
            ytd_gross=employee.ytd_gross,
        )

        federal_tax = taxes["federal_tax"]
        social_security = taxes["social_security"]
        medicare = taxes["medicare"]

        # Step 4: Calculate benefit deductions
        benefits = calculate_benefit_deductions(
            employee.benefits_elections, gross_pay
        )
        benefits_total = benefits["total"]

        # Step 5: Calculate totals
        total_deductions = (federal_tax + social_security + medicare +
                            benefits_total)

        # Net pay includes reimbursements (not taxable)
        net_pay = round(gross_pay - total_deductions +
                        pay_period.reimbursements, 2)

        # Step 6: Update YTD
        new_ytd_gross = employee.ytd_gross + gross_pay
        new_ytd_tax = employee.ytd_tax + federal_tax + social_security + medicare
        new_ytd_benefits = employee.ytd_benefits + benefits_total

        # Step 7: Build pay stub
        stub = PayStub(
            employee_id=employee.employee_id,
            period_start=pay_period.period_start,
            period_end=pay_period.period_end,
            regular_pay=round(regular_pay, 2),
            overtime_pay=round(overtime_pay, 2),
            shift_differential_pay=round(shift_diff_pay, 2),
            bonus=bonus,
            commission=commission,
            gross_pay=round(gross_pay, 2),
            federal_tax=federal_tax,
            social_security=social_security,
            medicare=medicare,
            benefits_deductions=benefits_total,
            total_deductions=round(total_deductions, 2),
            net_pay=net_pay,
            ytd_gross=round(new_ytd_gross, 2),
            ytd_tax=round(new_ytd_tax, 2),
            ytd_benefits=round(new_ytd_benefits, 2),
        )

        # Update employee YTD for next period
        employee.ytd_gross = new_ytd_gross
        employee.ytd_tax = new_ytd_tax
        employee.ytd_benefits = new_ytd_benefits

        return stub
