from app.models.calculator import CalculatorInputs, CalculationResult, TaxBreakdown
from app.utils.tax_constants import TAX_BRACKETS, NATIONAL_INSURANCE, HEALTH_TAX, CREDIT_POINTS, PENSION_RATES

class TaxCalculatorService:
    
    @staticmethod
    def calculate_income_tax(monthly_salary: float, credit_points: float) -> float:
        """Calculate monthly income tax based on brackets and credit points"""
        annual_salary = monthly_salary * 12
        annual_tax = 0
        
        for bracket in TAX_BRACKETS:
            if annual_salary > bracket["min"]:
                taxable_in_bracket = min(annual_salary, bracket["max"]) - bracket["min"]
                annual_tax += taxable_in_bracket * bracket["rate"]
        
        # Apply credit points (monthly reduction)
        monthly_tax = annual_tax / 12
        credit_reduction = credit_points * CREDIT_POINTS["basic"]
        
        return max(0, monthly_tax - credit_reduction)
    
    @staticmethod
    def calculate_national_insurance(monthly_salary: float) -> float:
        """Calculate national insurance contribution"""
        capped_salary = min(monthly_salary, NATIONAL_INSURANCE["max_salary"])
        if capped_salary < NATIONAL_INSURANCE["min_salary"]:
            return 0
        return capped_salary * NATIONAL_INSURANCE["employee_rate"]
    
    @staticmethod
    def calculate_health_tax(monthly_salary: float) -> float:
        """Calculate health tax contribution"""
        capped_salary = min(monthly_salary, HEALTH_TAX["max_salary"])
        return capped_salary * HEALTH_TAX["rate"]
    
    @staticmethod
    def calculate_pension(monthly_salary: float, pension_rate: float) -> float:
        """Calculate pension contribution"""
        capped_salary = min(monthly_salary, PENSION_RATES["max_salary"])
        rate = max(pension_rate / 100, PENSION_RATES["employee_min"])
        return capped_salary * rate
    
    @staticmethod
    def calculate_credit_points(inputs: CalculatorInputs) -> float:
        """Calculate total credit points"""
        points = 1  # Basic credit point
        
        if inputs.spouse:
            points += 1
        
        points += inputs.children
        
        if inputs.disabled:
            points += 1
        
        if inputs.new_immigrant:
            points += 1
        
        if inputs.student:
            points += 1
        
        if inputs.reserve_duty:
            points += 1
        
        return points
    
    @classmethod
    def calculate_net_salary(cls, inputs: CalculatorInputs) -> CalculationResult:
        """Main calculation method for employee salary"""
        gross_salary = inputs.gross_salary
        credit_points = cls.calculate_credit_points(inputs)
        
        # Calculate deductions
        income_tax = cls.calculate_income_tax(gross_salary, credit_points)
        national_insurance = cls.calculate_national_insurance(gross_salary)
        health_tax = cls.calculate_health_tax(gross_salary)
        pension_employee = cls.calculate_pension(gross_salary, inputs.pension_rate)
        
        total_deductions = income_tax + national_insurance + health_tax + pension_employee
        net_salary = gross_salary - total_deductions
        
        tax_breakdown = TaxBreakdown(
            income_tax=income_tax,
            national_insurance=national_insurance,
            health_tax=health_tax,
            pension_employee=pension_employee,
            total_deductions=total_deductions
        )
        
        effective_tax_rate = (total_deductions / gross_salary * 100) if gross_salary > 0 else 0
        
        return CalculationResult(
            gross_salary=gross_salary,
            net_salary=net_salary,
            tax_breakdown=tax_breakdown,
            credit_points=credit_points,
            effective_tax_rate=effective_tax_rate
        )
