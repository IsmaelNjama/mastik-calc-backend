from app.models.calculator import CalculatorInputs, CalculationResult, SelfEmploymentType
from app.services.tax_calculator import TaxCalculatorService

class SelfEmployedCalculatorService:
    
    @staticmethod
    def calculate_self_employed_income(inputs: CalculatorInputs) -> CalculationResult:
        """Calculate net income for self-employed individuals"""
        if not inputs.self_employed_income:
            raise ValueError("Self-employed income data is required")
        
        se_income = inputs.self_employed_income
        
        # Calculate net business income
        if se_income.actual_expenses:
            net_business_income = se_income.revenue - se_income.actual_expenses
        else:
            net_business_income = se_income.revenue * (1 - se_income.expense_rate / 100)
        
        # Convert to monthly for tax calculation
        monthly_income = net_business_income / 12
        
        # Apply different tax treatments based on business type
        if se_income.type == SelfEmploymentType.ESEK_PATUR:
            # Exempt business - reduced tax rates
            monthly_income *= 0.75  # Simplified reduction
        elif se_income.type == SelfEmploymentType.ESEK_ZAIR:
            # Small business - some benefits
            monthly_income *= 0.85  # Simplified reduction
        
        # Create input for tax calculation
        tax_inputs = CalculatorInputs(
            employment_type=inputs.employment_type,
            gross_salary=monthly_income,
            age=inputs.age,
            children=inputs.children,
            spouse=inputs.spouse,
            spouse_income=inputs.spouse_income,
            disabled=inputs.disabled,
            new_immigrant=inputs.new_immigrant,
            student=inputs.student,
            reserve_duty=inputs.reserve_duty,
            pension_rate=0  # Self-employed handle pension differently
        )
        
        result = TaxCalculatorService.calculate_net_salary(tax_inputs)
        
        # Adjust for annual calculation
        result.gross_salary = net_business_income
        result.net_salary = result.net_salary * 12
        result.tax_breakdown.income_tax *= 12
        result.tax_breakdown.national_insurance *= 12
        result.tax_breakdown.health_tax *= 12
        result.tax_breakdown.total_deductions *= 12
        
        return result
