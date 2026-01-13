# Israeli Tax Constants for 2025
# ANNUAL Income tax brackets (fixed 2025)
TAX_BRACKETS = [
    {"min": 0, "max": 83280, "rate": 0.10},
    {"min": 83281, "max": 119520, "rate": 0.14},
    {"min": 119521, "max": 191280, "rate": 0.20},
    {"min": 191281, "max": 264000, "rate": 0.31},
    {"min": 264001, "max": 660480, "rate": 0.35},
    {"min": 660481, "max": 1003920, "rate": 0.47},
    {"min": 1003921, "max": float('inf'), "rate": 0.50}
]


# Employees: different rates below and above 7,522 NIS
# Self-employed: different rates below and above 7,522 NIS
NATIONAL_INSURANCE = {
    # Employee rates (Bituach Leumi)
    "employee_tier1_threshold": 7522,     # Below this amount
    "employee_tier1_rate": 0.0427,        # 4.27% for employee up to 7,522
    "employee_tier2_rate": 0.1217,        # 12.17% for employee 7,522.01–50,695
    "max_salary": 50695,                  # Monthly ceiling (50,695 NIS)
    "min_salary": 7522,                   # Monthly minimum (7,522 NIS)

    # Employer rates (Bituach Leumi)
    "employer_tier1_rate": 0.0451,        # 4.51% for employer up to 7,522
    "employer_tier2_rate": 0.0760,        # 7.60% for employer 7,522.01–50,695

    # Self-employed rates (includes health insurance)
    "self_employed_tier1_threshold": 7522,
    "self_employed_tier1_rate": 0.0770,   # 7.70% up to 7,522
    "self_employed_tier2_rate": 0.18,     # 18% above 7,522 (includes health)
}

# Health tax rates (for employees only, self-employed included in National Insurance)
HEALTH_TAX = {
    "rate": 0.031,
    "max_salary": 48240
}

# Credit points monetary values (2025)
CREDIT_POINTS = {
    "value_point_month": 242,      # 242 NIS per month per point
    "value_point_year": 2904,      # 2,904 NIS per year per point
    # C_RESIDENT: Always 2.25 points (2 for residency + 0.25 travel compensation)
    "resident": 2.25,
}

# Pension rates - differentiated by employee/employer and employment type
PENSION_RATES = {
    # Employee rates
    "employee_min": 0.06,           # Minimum 6% for employees
    "employee_max": 1.0,            # Maximum rate

    # Employer rates (not deducted from employee, informational)
    "employer_pension": 0.065,      # 6.5% pension contribution
    "employer_severance": 0.06,     # 6% severance contribution

    # Self-employed rates
    "self_employed_tier1_threshold": 7122,  # Below this amount
    "self_employed_tier1_rate": 0.0445,     # 4.45% up to 7,122
    "self_employed_tier2_rate": 0.1255,     # Up to 12.55% above 7,122
    "self_employed_mandatory_threshold": 6331,  # Mandatory if income > 6,331/month

    # Maximum salary cap for calculations
    "max_salary": 48240
}
