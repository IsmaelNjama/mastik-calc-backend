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
    children: int = Field(ge=0, le=20, default=0)
    spouse: bool = Field(default=False)
    spouse_income: float = Field(ge=0, default=0)
    disabled: bool = Field(default=False)
    new_immigrant: bool = Field(default=False)
    student: bool = Field(default=False)
    reserve_duty: bool = Field(default=False)
    pension_rate: float = Field(ge=0, le=100, default=6)

class TaxBreakdown(BaseModel):
    income_tax: float
    national_insurance: float
    health_tax: float
    pension_employee: float
    total_deductions: float

class CalculationResult(BaseModel):
    gross_salary: float
    net_salary: float
    tax_breakdown: TaxBreakdown
    credit_points: float
    effective_tax_rate: float
