from fastapi import APIRouter, HTTPException
from app.models.calculator import CalculatorInputs, CalculationResult, EmploymentType
from app.services.tax_calculator import TaxCalculatorService
from app.services.multi_source_calculator import MultiSourceCalculatorService
from app.services.self_employed_calculator import SelfEmployedCalculatorService

router = APIRouter(prefix="/calculator", tags=["calculator"])

@router.post("/calculate", response_model=CalculationResult)
async def calculate_salary(inputs: CalculatorInputs):
    """Calculate net salary based on employment type and inputs"""
    try:
        if inputs.employment_type == EmploymentType.EMPLOYEE:
            return TaxCalculatorService.calculate_net_salary(inputs)
        
        elif inputs.employment_type == EmploymentType.MULTIPLE_EMPLOYERS:
            if not inputs.jobs:
                raise HTTPException(status_code=400, detail="Jobs data required for multiple employers")
            return MultiSourceCalculatorService.calculate_multiple_employers(inputs)
        
        elif inputs.employment_type == EmploymentType.COMBINED:
            if not inputs.self_employed_income:
                raise HTTPException(status_code=400, detail="Self-employed income data required for combined employment")
            return MultiSourceCalculatorService.calculate_combined_employment(inputs)
        
        elif inputs.employment_type == EmploymentType.SELF_EMPLOYED:
            if not inputs.self_employed_income:
                raise HTTPException(status_code=400, detail="Self-employed income data required")
            return SelfEmployedCalculatorService.calculate_self_employed_income(inputs)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid employment type")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tax-brackets")
async def get_tax_brackets():
    """Get current tax brackets"""
    from app.utils.tax_constants import TAX_BRACKETS
    return {"tax_brackets": TAX_BRACKETS}

@router.get("/constants")
async def get_tax_constants():
    """Get all tax constants"""
    from app.utils.tax_constants import NATIONAL_INSURANCE, HEALTH_TAX, CREDIT_POINTS, PENSION_RATES
    return {
        "national_insurance": NATIONAL_INSURANCE,
        "health_tax": HEALTH_TAX,
        "credit_points": CREDIT_POINTS,
        "pension_rates": PENSION_RATES
    }
