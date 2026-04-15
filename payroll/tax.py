"""Federal income tax calculation with progressive brackets."""

# Federal tax brackets (2024, simplified for single filers)
# Each tuple: (lower_bound, upper_bound, rate)
TAX_BRACKETS = [
    (0,      11600,   0.10),
    (11600,  47150,   0.12),
    (47150,  100525,  0.22),
    (100525, 191950,  0.24),
    (191950, 243725,  0.32),
    (243725, 609350,  0.35),
    (609350, None,    0.37),
]

# Social Security and Medicare rates
SOCIAL_SECURITY_RATE = 0.062
SOCIAL_SECURITY_WAGE_BASE = 168600  # 2024 limit
MEDICARE_RATE = 0.0145
MEDICARE_ADDITIONAL_RATE = 0.009  # Additional Medicare on wages > 200k
MEDICARE_ADDITIONAL_THRESHOLD = 200000


def get_tax_rate(annual_income: float) -> float:
    """Get the marginal tax rate for a given annual income.

    Returns the rate of the highest bracket that the income falls into.
    """
    for lower, upper, rate in TAX_BRACKETS:
        if upper is None or annual_income <= upper:
            return rate
    return TAX_BRACKETS[-1][2]


def calculate_marginal_tax(annual_income: float) -> float:
    """Calculate federal income tax using marginal/progressive brackets.

    Each portion of income within a bracket is taxed at that bracket's
    rate. For example, income of $50,000 is taxed:
      - First $11,600 at 10% = $1,160
      - Next $35,550 ($11,600 to $47,150) at 12% = $4,266
      - Remaining $2,850 ($47,150 to $50,000) at 22% = $627
      - Total: $6,053
    """
    # BUG: Uses flat rate based on top bracket instead of progressive calculation
    rate = get_tax_rate(annual_income)
    return round(annual_income * rate, 2)


def calculate_tax(gross_pay: float, pay_periods_per_year: int = 26,
                  ytd_gross: float = 0.0) -> dict:
    """Calculate all payroll taxes for a single pay period.

    Projects the pay period's gross to an annual figure to determine
    the correct tax bracket, then calculates the per-period tax amount.

    Args:
        gross_pay: Gross pay for this pay period
        pay_periods_per_year: Number of pay periods (26 for biweekly)
        ytd_gross: Year-to-date gross before this period
    """
    # Project annual income for bracket determination
    projected_annual = gross_pay * pay_periods_per_year

    # Calculate annualized federal tax, then divide by periods
    annual_tax = calculate_marginal_tax(projected_annual)
    federal_tax = round(annual_tax / pay_periods_per_year, 2)

    # Social Security (6.2%, up to wage base)
    ytd_ss_wages = min(ytd_gross, SOCIAL_SECURITY_WAGE_BASE)
    remaining_ss_wages = max(0, SOCIAL_SECURITY_WAGE_BASE - ytd_ss_wages)
    ss_taxable = min(gross_pay, remaining_ss_wages)
    social_security = round(ss_taxable * SOCIAL_SECURITY_RATE, 2)

    # Medicare (1.45%, plus 0.9% additional over $200k)
    medicare = round(gross_pay * MEDICARE_RATE, 2)
    if ytd_gross + gross_pay > MEDICARE_ADDITIONAL_THRESHOLD:
        additional_wages = max(0, ytd_gross + gross_pay - MEDICARE_ADDITIONAL_THRESHOLD)
        additional_this_period = min(additional_wages, gross_pay)
        medicare += round(additional_this_period * MEDICARE_ADDITIONAL_RATE, 2)

    return {
        "federal_tax": federal_tax,
        "social_security": social_security,
        "medicare": medicare,
    }
