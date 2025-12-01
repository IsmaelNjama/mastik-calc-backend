from typing import List
from app.models.calculator import CalculatorInputs, JobIncome, CalculationResult
from app.services.tax_calculator import TaxCalculatorService

class MultiSourceCalculatorService:
    
    @staticmethod
    def calculate_multiple_employers(inputs: CalculatorInputs) -> CalculationResult:
        """Calculate net salary for multiple employers"""
        total_gross = sum(job.gross_salary for job in inputs.jobs)
        
        # Create a combined input for tax calculation
        combined_inputs = CalculatorInputs(
            employment_type=inputs.employment_type,
            gross_salary=total_gross,
            age=inputs.age,
            children=inputs.children,
            spouse=inputs.spouse,
            spouse_income=inputs.spouse_income,
            disabled=inputs.disabled,
            new_immigrant=inputs.new_immigrant,
            student=inputs.student,
            reserve_duty=inputs.reserve_duty,
            pension_rate=inputs.pension_rate
        )
        
        return TaxCalculatorService.calculate_net_salary(combined_inputs)
    
    @staticmethod
    def calculate_combined_employment(inputs: CalculatorInputs) -> CalculationResult:
        """Calculate net salary for combined employee + self-employed"""
        employee_gross = inputs.gross_salary
        
        # Calculate self-employed income
        if inputs.self_employed_income:
            se_income = inputs.self_employed_income
            if se_income.actual_expenses:
                se_net_income = se_income.revenue - se_income.actual_expenses
            else:
                se_net_income = se_income.revenue * (1 - se_income.expense_rate / 100)
        else:
            se_net_income = 0
        
        total_gross = employee_gross + se_net_income
        
        # Create combined input for tax calculation
        combined_inputs = CalculatorInputs(
            employment_type=inputs.employment_type,
            gross_salary=total_gross,
            age=inputs.age,
            children=inputs.children,
            spouse=inputs.spouse,
            spouse_income=inputs.spouse_income,
            disabled=inputs.disabled,
            new_immigrant=inputs.new_immigrant,
            student=inputs.student,
            reserve_duty=inputs.reserve_duty,
            pension_rate=inputs.pension_rate
        )
        
        return TaxCalculatorService.calculate_net_salary(combined_inputs)
