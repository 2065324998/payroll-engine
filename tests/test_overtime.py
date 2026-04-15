"""Tests for overtime calculation module."""

import pytest
from payroll.overtime import calculate_overtime_pay, OVERTIME_MULTIPLIER
from payroll.employee import ShiftHours


class TestOvertimePay:
    def test_no_overtime(self):
        shifts = [ShiftHours("day", regular_hours=40, overtime_hours=0)]
        result = calculate_overtime_pay(shifts, base_hourly_rate=20.0)
        assert result["regular_pay"] == 800.0
        assert result["overtime_pay"] == 0.0

    def test_day_shift_overtime(self):
        """Overtime on day shift only — base rate applies."""
        shifts = [ShiftHours("day", regular_hours=40, overtime_hours=10)]
        result = calculate_overtime_pay(shifts, base_hourly_rate=20.0)
        assert result["regular_pay"] == 800.0
        # Day shift only: overtime = 10 * 20 * 1.5 = 300
        assert result["overtime_pay"] == 300.0

    def test_shift_differential(self):
        """Night shift hours get 15% premium."""
        shifts = [ShiftHours("night", regular_hours=40, overtime_hours=0)]
        result = calculate_overtime_pay(shifts, base_hourly_rate=20.0)
        # Regular: 40 * 20 = 800
        # Differential: 40 * (23 - 20) = 120
        assert result["regular_pay"] == 800.0
        assert result["shift_differential_pay"] == 120.0

    def test_multiple_shifts_no_overtime(self):
        """Multiple shift types, no overtime."""
        shifts = [
            ShiftHours("day", regular_hours=30, overtime_hours=0),
            ShiftHours("night", regular_hours=10, overtime_hours=0),
        ]
        result = calculate_overtime_pay(shifts, base_hourly_rate=20.0)
        assert result["regular_pay"] == 800.0  # 40 * 20
        assert result["shift_differential_pay"] == 30.0  # 10 * 3
        assert result["total_regular_hours"] == 40
        assert result["total_overtime_hours"] == 0
