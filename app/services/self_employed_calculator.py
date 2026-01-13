from app.models.calculator import CalculatorInputs, CalculationResult, SelfEmploymentType
from app.services.tax_calculator import TaxCalculatorService


class SelfEmployedCalculatorService:

    @staticmethod
    def calculate_self_employed_income(inputs: CalculatorInputs) -> CalculationResult:
        """
        Calculate net income for self-employed individuals.
        """
        if not inputs.self_employed_income:
            raise ValueError("Self-employed income data is required")

        se_income = inputs.self_employed_income

        # Calculate net business income
        if se_income.actual_expenses:
            net_business_income = se_income.revenue - se_income.actual_expenses
        else:
            net_business_income = se_income.revenue * \
                (1 - se_income.expense_rate / 100)

        # Convert to monthly for tax calculation
        monthly_income = net_business_income / 12

        # Create input for tax calculation
        tax_inputs = CalculatorInputs(
            employment_type=inputs.employment_type,
            gross_salary=monthly_income,
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
            pension_rate=0
        )

        result = TaxCalculatorService.calculate_net_salary(tax_inputs)

        # Adjust for annual calculation
        result.gross_salary = net_business_income
        result.net_salary = result.net_salary * 12
        result.tax_breakdown.income_tax *= 12
        result.tax_breakdown.national_insurance_employee *= 12
        result.tax_breakdown.national_insurance_employer *= 12
        result.tax_breakdown.health_tax *= 12
        result.tax_breakdown.pension_employee *= 12
        result.tax_breakdown.pension_employer *= 12
        result.tax_breakdown.total_deductions *= 12

        return result
