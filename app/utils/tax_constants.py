# Israeli Tax Constants for 2025
TAX_BRACKETS = [
    {"min": 0, "max": 8880, "rate": 0.10},
    {"min": 8880, "max": 12720, "rate": 0.14},
    {"min": 12720, "max": 20440, "rate": 0.20},
    {"min": 20440, "max": 42030, "rate": 0.31},
    {"min": 42030, "max": 54130, "rate": 0.35},
    {"min": 54130, "max": float('inf'), "rate": 0.47}
]

# National Insurance rates (monthly)
NATIONAL_INSURANCE = {
    "employee_rate": 0.04,
    "max_salary": 48240,  # Monthly ceiling
    "min_salary": 7522    # Monthly minimum
}

# Health tax rates
HEALTH_TAX = {
    "rate": 0.031,
    "max_salary": 48240
}

# Credit points (monthly values)
CREDIT_POINTS = {
    "basic": 2.25,
    "spouse": 2.25,
    "child": 2.25,
    "disabled": 2.25,
    "new_immigrant": 2.25,
    "student": 2.25,
    "reserve_duty": 2.25
}

# Pension rates
PENSION_RATES = {
    "employee_min": 0.06,
    "employer": 0.075,
    "max_salary": 48240
}
