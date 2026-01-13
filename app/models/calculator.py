from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class EmploymentType(str, Enum):
    EMPLOYEE = "employee"
    SELF_EMPLOYED = "self_employed"
    COMBINED = "combined"
    MULTIPLE_EMPLOYERS = "multiple_employers"


class SelfEmploymentType(str, Enum):
    ESEK_PATUR = "esek_patur"
    ESEK_MURSHE = "esek_murshe"
    ESEK_ZAIR = "esek_zair"


class JobIncome(BaseModel):
    id: str
    gross_salary: float = Field(gt=0)
    pension_rate: float = Field(ge=0, le=100)
    credit_points_percent: float = Field(ge=0, le=100)


class SelfEmployedIncome(BaseModel):
    type: SelfEmploymentType
    revenue: float = Field(gt=0)
    expense_rate: float = Field(ge=0, le=100, default=30)
    actual_expenses: Optional[float] = None


class CalculatorInputs(BaseModel):
    employment_type: EmploymentType
    gross_salary: float = Field(default=0, ge=0)
    pension_base: Optional[float] = None
    jobs: List[JobIncome] = Field(default_factory=list)
    self_employed_income: Optional[SelfEmployedIncome] = None
    age: int = Field(ge=18, le=120)
    # Gender field - required for C_WOMAN and C_FOREIGN_WORKER credit calculations
    gender: str = Field(default="other")
    children: int = Field(ge=0, le=20, default=0)
    # Children ages - required for age-based child credit calculation per spec
    children_ages: List[int] = Field(default_factory=list)
    spouse: bool = Field(default=False)
    # Spouse dependent status - required to verify dependency conditions
    spouse_dependent: bool = Field(default=False)
    spouse_income: float = Field(ge=0, default=0)
    # Disability percentage - required for C_CHILDREN_SPECIAL_NEEDS validation (50%+, 74%+, 90%+)
    disability_percent: Optional[int] = Field(default=None)
    disabled: bool = Field(default=False)
    # Single parent status - required for C_SINGLE_PARENT calculation (1 point per child)
    is_single_parent: bool = Field(default=False)
    is_widow_widower: bool = Field(default=False)
    # Disabled dependents - required for C_CHILDREN_SPECIAL_NEEDS (2 points each)
    disabled_dependents: int = Field(ge=0, default=0)
    # Alimony payment - required for C_ALIMONY_EX_SPOUSE calculation
    alimony_payment: float = Field(ge=0, default=0)
    # Child support payment - required for C_CHILD_SUPPORT calculation
    child_support_payment: float = Field(ge=0, default=0)
    new_immigrant: bool = Field(default=False)
    # Date of aliyah - required for C_OLIM calculation (42 or 54 months rules)
    date_of_aliyah: Optional[str] = Field(default=None)
    student: bool = Field(default=False)
    # Education level - required for C_EDUCATION (BA/MA/PhD/Teaching/Medical)
    education_level: Optional[str] = Field(default=None)
    # Years active in education - required to calculate education credits (max 3 for BA, 2 for MA/PhD)
    education_years_active: int = Field(ge=0, default=0)
    # Professional training - required for C_PROFESSIONAL_TRAINING calculation
    professional_training: bool = Field(default=False)
    reserve_duty: bool = Field(default=False)
    # Foreign worker status - required for C_FOREIGN_WORKER calculation
    foreign_worker: bool = Field(default=False)
    # Foreign worker type - 'caregiver' (2.25 points) or 'other' (1 point)
    foreign_worker_type: Optional[str] = Field(default=None)
    #  City - required for city tax relief (issue #7)
    city: Optional[str] = Field(default=None)
    pension_rate: float = Field(ge=0, le=100, default=6)


class TaxBreakdown(BaseModel):
    # Separated employee and employer contributions
    income_tax: float
    national_insurance_employee: float  # ISSUE #4 & #5: Employee portion per spec
    # Employer portion (not deducted from employee)
    national_insurance_employer: float
    health_tax: float
    pension_employee: float  # ISSUE #5: Employee contribution
    # Employer contribution (not deducted from employee)
    pension_employer: float
    total_deductions: float  # Employee deductions only


class CalculationResult(BaseModel):
    gross_salary: float
    net_salary: float
    tax_breakdown: TaxBreakdown
    # Credit points as number (not monetary value)
    credit_points: float
    # Monetary value of credits using 2025 constants (242 NIS/month)
    tax_credit_annual: float
    tax_credit_monthly: float
    effective_tax_rate: float
