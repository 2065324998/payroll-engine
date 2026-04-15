"""Employee and payroll data structures."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class ShiftHours:
    """Hours worked in a specific shift type."""
    shift_type: str  # "day", "evening", "night"
    regular_hours: float
    overtime_hours: float


@dataclass
class PayPeriod:
    """Represents a single pay period's work data."""
    period_start: date
    period_end: date
    shifts: list[ShiftHours] = field(default_factory=list)
    bonus: float = 0.0
    commission: float = 0.0
    reimbursements: float = 0.0

    @property
    def total_regular_hours(self) -> float:
        return sum(s.regular_hours for s in self.shifts)

    @property
    def total_overtime_hours(self) -> float:
        return sum(s.overtime_hours for s in self.shifts)

    @property
    def total_hours(self) -> float:
        return self.total_regular_hours + self.total_overtime_hours


@dataclass
class Employee:
    """Employee record with compensation details."""
    employee_id: str
    name: str
    base_hourly_rate: float
    filing_status: str = "single"  # "single", "married", "head_of_household"
    exemptions: int = 1
    benefits_elections: dict = field(default_factory=dict)
    ytd_gross: float = 0.0
    ytd_tax: float = 0.0
    ytd_benefits: float = 0.0


# Shift differential rates (multiplied by base hourly rate)
SHIFT_DIFFERENTIALS = {
    "day": 1.0,
    "evening": 1.10,   # 10% premium
    "night": 1.15,     # 15% premium
    "weekend": 1.25,   # 25% premium
}


@dataclass
class PayStub:
    """A completed pay stub for one pay period."""
    employee_id: str
    period_start: date
    period_end: date

    # Earnings
    regular_pay: float = 0.0
    overtime_pay: float = 0.0
    shift_differential_pay: float = 0.0
    bonus: float = 0.0
    commission: float = 0.0
    gross_pay: float = 0.0

    # Deductions
    federal_tax: float = 0.0
    state_tax: float = 0.0
    social_security: float = 0.0
    medicare: float = 0.0
    benefits_deductions: float = 0.0
    total_deductions: float = 0.0

    # Net
    net_pay: float = 0.0

    # YTD
    ytd_gross: float = 0.0
    ytd_tax: float = 0.0
    ytd_benefits: float = 0.0
