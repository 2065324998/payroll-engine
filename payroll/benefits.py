"""Employee benefits deduction calculations."""


# Benefits options and per-pay-period costs
BENEFITS_CATALOG = {
    "health_basic": {
        "name": "Basic Health Insurance",
        "employee_cost": 125.00,  # per pay period
        "employer_cost": 375.00,
    },
    "health_premium": {
        "name": "Premium Health Insurance",
        "employee_cost": 225.00,
        "employer_cost": 575.00,
    },
    "dental": {
        "name": "Dental Insurance",
        "employee_cost": 35.00,
        "employer_cost": 65.00,
    },
    "vision": {
        "name": "Vision Insurance",
        "employee_cost": 15.00,
        "employer_cost": 25.00,
    },
    "401k": {
        "name": "401(k) Retirement",
        "employee_cost": None,  # percentage-based, set at election
        "employer_match": 0.50,  # 50% match up to 6%
        "match_limit": 0.06,
    },
    "hsa": {
        "name": "Health Savings Account",
        "employee_cost": None,  # employee-set contribution
    },
    "life_insurance": {
        "name": "Basic Life Insurance",
        "employee_cost": 12.50,
        "employer_cost": 37.50,
    },
}


def calculate_benefit_deductions(elections: dict,
                                  gross_pay: float) -> dict:
    """Calculate benefit deductions for a pay period.

    Elections is a dict mapping benefit_id to either True (for
    fixed-cost benefits) or a value (for percentage-based benefits
    like 401k contribution percentage).

    Returns a dict with per-benefit deductions and total.
    """
    deductions = {}
    total = 0.0

    for benefit_id, election in elections.items():
        if benefit_id not in BENEFITS_CATALOG:
            continue

        benefit = BENEFITS_CATALOG[benefit_id]

        if benefit_id == "401k":
            # Percentage of gross pay
            contribution_pct = float(election) if election else 0.0
            amount = round(gross_pay * contribution_pct, 2)
            deductions[benefit_id] = amount
            total += amount

        elif benefit_id == "hsa":
            # Fixed dollar amount per period
            amount = float(election) if election else 0.0
            deductions[benefit_id] = round(amount, 2)
            total += round(amount, 2)

        else:
            # Fixed-cost benefit
            if election:
                amount = benefit["employee_cost"]
                deductions[benefit_id] = amount
                total += amount

    return {
        "deductions": deductions,
        "total": round(total, 2),
    }
