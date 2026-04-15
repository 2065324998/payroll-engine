"""Overtime pay calculation with shift differential support."""

from payroll.employee import ShiftHours, SHIFT_DIFFERENTIALS

# Federal overtime multiplier (time and a half)
OVERTIME_MULTIPLIER = 1.5


def calculate_overtime_pay(shifts: list[ShiftHours],
                           base_hourly_rate: float) -> dict:
    """Calculate overtime pay considering shift differentials.

    When an employee works multiple shift types and earns overtime,
    the overtime rate should be based on the weighted average of
    all shift rates worked during the period, not just the base rate.

    For example, if an employee works:
      - 30 regular hours on day shift ($20/hr base)
      - 10 regular hours on night shift ($20 * 1.15 = $23/hr)
      - 5 overtime hours

    The blended regular rate is:
      (30 * $20 + 10 * $23) / 40 = $20.75/hr

    Overtime rate: $20.75 * 1.5 = $31.125/hr
    Overtime pay: 5 * $31.125 = $155.63

    Returns a dict with regular_pay, overtime_pay, shift_differential_pay.
    """
    total_regular_hours = sum(s.regular_hours for s in shifts)
    total_overtime_hours = sum(s.overtime_hours for s in shifts)

    # Calculate regular pay per shift with differentials
    regular_pay = 0.0
    shift_differential_pay = 0.0

    for shift in shifts:
        diff_rate = SHIFT_DIFFERENTIALS.get(shift.shift_type, 1.0)
        shift_rate = base_hourly_rate * diff_rate
        base_pay = shift.regular_hours * base_hourly_rate
        diff_pay = shift.regular_hours * (shift_rate - base_hourly_rate)
        regular_pay += base_pay
        shift_differential_pay += diff_pay

    # Calculate overtime rate and pay
    overtime_rate = base_hourly_rate * OVERTIME_MULTIPLIER
    overtime_pay = round(total_overtime_hours * overtime_rate, 2)

    return {
        "regular_pay": round(regular_pay, 2),
        "overtime_pay": overtime_pay,
        "shift_differential_pay": round(shift_differential_pay, 2),
        "total_regular_hours": total_regular_hours,
        "total_overtime_hours": total_overtime_hours,
    }
