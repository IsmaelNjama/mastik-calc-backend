from typing import List
from app.models.calculator import CalculatorInputs, JobIncome, CalculationResult
from app.services.tax_calculator import TaxCalculatorService


class MultiSourceCalculatorService:

    @staticmethod
    def calculate_multiple_employers(inputs: CalculatorInputs) -> CalculationResult:
        """
        Calculate net salary for multiple employers.
        """
        total_gross = sum(job.gross_salary for job in inputs.jobs)

        # Create a combined input for tax calculation
        combined_inputs = CalculatorInputs(
            employment_type=inputs.employment_type,
            gross_salary=total_gross,
            age=inputs.age,
            gender=inputs.gender,
            children=inputs.children,
            children_ages=inputs.children_ages,
            spouse=inputs.spouse,
            spouse_dependent=inputs.spouse_dependent,
            spouse_income=inputs.spouse_income,
            disability_percent=inputs.disability_percent,
            disabled=inputs.disabled,
            is_single_parent=inputs.is_single_parent,
            is_widow_widower=inputs.is_widow_widower,
            disabled_dependents=inputs.disabled_dependents,
            alimony_payment=inputs.alimony_payment,
            child_support_payment=inputs.child_support_payment,
            new_immigrant=inputs.new_immigrant,
            date_of_aliyah=inputs.date_of_aliyah,
            student=inputs.student,
            education_level=inputs.education_level,
            education_years_active=inputs.education_years_active,
            professional_training=inputs.professional_training,
            reserve_duty=inputs.reserve_duty,
            foreign_worker=inputs.foreign_worker,
            foreign_worker_type=inputs.foreign_worker_type,
            city=inputs.city,
            pension_rate=inputs.pension_rate
        )

        return TaxCalculatorService.calculate_net_salary(combined_inputs)

    @staticmethod
    def calculate_combined_employment(inputs: CalculatorInputs) -> CalculationResult:
        """
        Calculate net salary for combined employee + self-employed.
        """
        employee_gross = inputs.gross_salary

        # Calculate self-employed income
        if inputs.self_employed_income:
            se_income = inputs.self_employed_income
            if se_income.actual_expenses:
                se_net_income = se_income.revenue - se_income.actual_expenses
            else:
                se_net_income = se_income.revenue * \
                    (1 - se_income.expense_rate / 100)
        else:
            se_net_income = 0

        total_gross = employee_gross + se_net_income

        # Create combined input for tax calculation
        combined_inputs = CalculatorInputs(
            employment_type=inputs.employment_type,
            gross_salary=total_gross,
            age=inputs.age,
            gender=inputs.gender,
            children=inputs.children,
            children_ages=inputs.children_ages,
            spouse=inputs.spouse,
            spouse_dependent=inputs.spouse_dependent,
            spouse_income=inputs.spouse_income,
            disability_percent=inputs.disability_percent,
            disabled=inputs.disabled,
            is_single_parent=inputs.is_single_parent,
            is_widow_widower=inputs.is_widow_widower,
            disabled_dependents=inputs.disabled_dependents,
            alimony_payment=inputs.alimony_payment,
            child_support_payment=inputs.child_support_payment,
            new_immigrant=inputs.new_immigrant,
            date_of_aliyah=inputs.date_of_aliyah,
            student=inputs.student,
            education_level=inputs.education_level,
            education_years_active=inputs.education_years_active,
            professional_training=inputs.professional_training,
            reserve_duty=inputs.reserve_duty,
            foreign_worker=inputs.foreign_worker,
            foreign_worker_type=inputs.foreign_worker_type,
            city=inputs.city,
            pension_rate=inputs.pension_rate
        )

        return TaxCalculatorService.calculate_net_salary(combined_inputs)
