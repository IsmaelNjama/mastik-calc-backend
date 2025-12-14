# ============================================================
# ISRAEL TAX CONSTANTS 2025 (MONTHLY)
# All monetary values are in NIS
# ============================================================


# ------------------------------------------------------------
# INCOME TAX (Mas Hachnasa)
# MONTHLY tax brackets
# ------------------------------------------------------------

TAX_BRACKETS_MONTHLY = [
    {"min": 0,       "max": 6940,     "rate": 0.10},
    {"min": 6940,    "max": 9960,     "rate": 0.14},
    {"min": 9960,    "max": 15940,    "rate": 0.20},
    {"min": 15940,   "max": 22000,    "rate": 0.31},
    {"min": 22000,   "max": 55040,    "rate": 0.35},
    {"min": 55040,   "max": 83660,    "rate": 0.47},
    {"min": 83660,   "max": float("inf"), "rate": 0.50},
]


# ------------------------------------------------------------
# BITUACH LEUMI (National Insurance)
# Monthly thresholds and rates
# ------------------------------------------------------------

BITUACH_LEUMI = {
    "employee": [
        {"min": 0,     "max": 7122,   "rate": 0.035},
        {"min": 7122,  "max": 47465,  "rate": 0.12},
    ],
    "employer": [
        {"min": 0,     "max": 7122,   "rate": 0.0355},
        {"min": 7122,  "max": 47465,  "rate": 0.076},
    ],
    "self_employed": [
        {"min": 0,     "max": 7122,   "rate": 0.0597},
        {"min": 7122,  "max": 47465,  "rate": 0.1783},
    ],
}


# ------------------------------------------------------------
# PENSION CONTRIBUTIONS
# Monthly rates
# ------------------------------------------------------------

PENSION = {
    "employee_rate": 0.06,
    "employer_pension_rate": 0.065,
    "employer_severance_rate": 0.06,

    "self_employed": {
        "mandatory_if_income_over": 6331,
        "threshold": 7122,
        "rate_below_threshold": 0.0445,
        "rate_above_threshold_max": 0.1255,
    },
}


# ------------------------------------------------------------
# CREDIT POINTS (Nekudot Zikuy)
# ------------------------------------------------------------

CREDIT_POINTS = {
    "POINT_VALUE_MONTH": 242,
    "POINT_VALUE_YEAR": 2904,
    "POINT_VALUE_HALF_MONTH": 121,
    "POINT_VALUE_QUARTER_MONTH": 60.5,

    "C_RESIDENT": 2.25,
    "C_WOMAN": 0.5,
    "C_WORKING_TEEN": 1.0,

    "C_DEPENDENT_SPOUSE": {
        "joint_filing": 1.0,
        "separate_filing": 0.5,
    },

    "C_ALIMONY_EX_SPOUSE": 1.0,

    "C_FOREIGN_WORKER": {
        "caregiver": 2.25,
        "other": 1.0,
        "female_extra": 0.5,
    },
}


# ------------------------------------------------------------
# CREDIT POINTS – CHILDREN RULES
# ------------------------------------------------------------

CHILD_CREDIT_RULES = {
    "AGE_0_5": {
        "min_age": 0,
        "max_age": 5,
        "points_per_child": 1.5,
        "granted_to": "mother",
        "from_birth_month": True,
    },

    "AGE_6_17": {
        "min_age": 6,
        "max_age": 17,
        "points_per_child": 1.0,
        "granted_to": "mother",
    },

    "AGE_18": {
        "min_age": 18,
        "max_age": 18,
        "points_per_child": 0.5,
        "granted_to": "dependent_parent",
        "only_in_year_of_age": 18,
    },

    "SPECIAL_NEEDS_CHILD": {
        "points_per_child": 2.0,
        "independent_of_age": True,
        "requires_official_recognition": True,
    },

    "SINGLE_PARENT_EXTRA": {
        "points_per_child": 1.0,
        "condition": "single_parent_and_child_lives_with_parent",
    },

    "TRANSFER_RULES": {
        "default_holder": "mother",
        "father_possible_if_mother_waives": True,
        "partial_transfer_allowed": True,
    },
}


VAT = {
    "rate": 0.18
}