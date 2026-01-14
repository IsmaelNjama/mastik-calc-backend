from app.models.calculator import CalculatorInputs, CalculationResult, TaxBreakdown
from app.utils.tax_constants import TAX_BRACKETS, NATIONAL_INSURANCE, HEALTH_TAX, CREDIT_POINTS, PENSION_RATES
from datetime import datetime
from typing import Tuple


class TaxCalculatorService:

    # National Insurance calculation with two-tier structure
    @staticmethod
    def calculate_national_insurance_employee(monthly_salary: float, is_self_employed: bool = False) -> float:
        """
        Calculate national insurance contribution for employee.
        Implements two-tier structure per spec section 6:
        - Tier 1 (up to 7,522): 4.27% for employee
        - Tier 2 (7,522.01–50,695): 12.17% for employee
        """
        if is_self_employed:
            # Self-employed calculation
            capped_salary = min(
                monthly_salary, NATIONAL_INSURANCE["max_salary"])
            threshold = NATIONAL_INSURANCE["self_employed_tier1_threshold"]

            if capped_salary <= threshold:
                return capped_salary * NATIONAL_INSURANCE["self_employed_tier1_rate"]
            else:
                tier1_amount = threshold * \
                    NATIONAL_INSURANCE["self_employed_tier1_rate"]
                tier2_amount = (capped_salary - threshold) * \
                    NATIONAL_INSURANCE["self_employed_tier2_rate"]
                return tier1_amount + tier2_amount
        else:
            # Employee calculation
            capped_salary = min(
                monthly_salary, NATIONAL_INSURANCE["max_salary"])
            if capped_salary < NATIONAL_INSURANCE["min_salary"]:
                return 0

            threshold = NATIONAL_INSURANCE["employee_tier1_threshold"]

            if capped_salary <= threshold:
                return capped_salary * NATIONAL_INSURANCE["employee_tier1_rate"]
            else:
                tier1_amount = threshold * \
                    NATIONAL_INSURANCE["employee_tier1_rate"]
                tier2_amount = (capped_salary - threshold) * \
                    NATIONAL_INSURANCE["employee_tier2_rate"]
                return tier1_amount + tier2_amount

    # Employer National Insurance calculation
    @staticmethod
    def calculate_national_insurance_employer(monthly_salary: float) -> float:
        """
        Calculate employer National Insurance contribution (informational only, not deducted from employee).
        Employer contributions:
        - Tier 1 (up to 7,522): 4.51% for employer
        - Tier 2 (7,522.01–50,695): 7.60% for employer
        """
        capped_salary = min(monthly_salary, NATIONAL_INSURANCE["max_salary"])
        if capped_salary < NATIONAL_INSURANCE["min_salary"]:
            return 0

        threshold = NATIONAL_INSURANCE["employee_tier1_threshold"]

        if capped_salary <= threshold:
            return capped_salary * NATIONAL_INSURANCE["employer_tier1_rate"]
        else:
            tier1_amount = threshold * \
                NATIONAL_INSURANCE["employer_tier1_rate"]
            tier2_amount = (capped_salary - threshold) * \
                NATIONAL_INSURANCE["employer_tier2_rate"]
            return tier1_amount + tier2_amount

    @staticmethod
    def calculate_health_tax(monthly_salary: float) -> float:
        """Calculate health tax contribution"""
        capped_salary = min(monthly_salary, HEALTH_TAX["max_salary"])
        return capped_salary * HEALTH_TAX["rate"]

    # pension calculation to differentiate employee and employer
    @staticmethod
    def calculate_pension_employee(monthly_salary: float, pension_rate: float, is_self_employed: bool = False) -> float:
        """
        Calculate employee pension contribution (deducted from salary).
        Employee contribution per spec section 7: 6% for employees
        """
        if is_self_employed:
            return TaxCalculatorService.calculate_pension_self_employed(monthly_salary)

        capped_salary = min(monthly_salary, PENSION_RATES["max_salary"])
        rate = max(pension_rate / 100, PENSION_RATES["employee_min"])
        return capped_salary * rate

    @staticmethod
    def calculate_pension_employer(monthly_salary: float) -> float:
        """
        Calculate employer pension contribution (informational only, not deducted from employee).

        """
        capped_salary = min(monthly_salary, PENSION_RATES["max_salary"])
        employer_total_rate = PENSION_RATES["employer_pension"] + \
            PENSION_RATES["employer_severance"]
        return capped_salary * employer_total_rate

    @staticmethod
    def calculate_pension_self_employed(monthly_income: float) -> float:
        """
        Calculate self-employed pension contribution.

        - 4.45% up to 7,122 NIS
        - Up to 12.55% above 7,122 NIS
        - Mandatory if income > 6,331/month
        """
        threshold = PENSION_RATES["self_employed_tier1_threshold"]

        if monthly_income <= threshold:
            return monthly_income * PENSION_RATES["self_employed_tier1_rate"]
        else:
            tier1_amount = threshold * \
                PENSION_RATES["self_employed_tier1_rate"]
            tier2_amount = (monthly_income - threshold) * \
                PENSION_RATES["self_employed_tier2_rate"]
            return tier1_amount + tier2_amount

    @staticmethod
    def calculate_credit_points(inputs: CalculatorInputs) -> float:
        """
        Calculate total tax credit points per spec (Nekudot Zikuy).
        Implements comprehensive spec with all credit categories:
        - C_RESIDENT: 2.25 points (mandatory for residents)
        - C_WOMAN: 0.5 points (working women)
        - C_WORKING_TEEN: 1 point (ages 16-18)
        - C_FOREIGN_WORKER: 2.25 (caregiver) or 1 (other)
        - C_OLIM: 1-3 points (new immigrants, based on arrival date)
        - C_SPOUSE_DEPENDENT: 1 or 0.5 points (dependent spouse with conditions)
        - C_ALIMONY_EX_SPOUSE: 1 point (paying alimony)
        - C_CHILDREN: Complex calculation (1-2.5 points per child based on age)
        - C_CHILDREN_SPECIAL_NEEDS: 2 points per disabled dependent
        - C_SINGLE_PARENT: 1 point per child
        - C_CHILD_SUPPORT: 1 point
        - C_EDUCATION: Up to 3 years, 1 point/year (BA) or 0.5 points/year (MA/PhD)
        - C_PROFESSIONAL_TRAINING: Up to 3 years, 1 point/year
        """
        points = 0.0
        print("Calculating credit points for inputs:", inputs)

        # C_RESIDENT: Always 2.25 for Israeli residents with taxable income
        points += CREDIT_POINTS["resident"]
        print("points resident res", points)

        # C_WOMAN: 0.5 points for working women
        if inputs.gender and inputs.gender.lower() in ["female", "woman", "f"]:
            points += 0.5
            print("points female res", points)

        # C_WORKING_TEEN: 1 point for teenagers aged 16-18 with taxable income
        if 16 <= inputs.age <= 18:
            points += 1.0

        # C_FOREIGN_WORKER: 2.25 (caregiver) or 1 (other) + 0.5 if female
        if inputs.foreign_worker:
            if inputs.foreign_worker_type and inputs.foreign_worker_type.lower() == "caregiver":
                points += 2.25
            else:
                points += 1.0
            if inputs.gender and inputs.gender.lower() in ["female", "woman", "f"]:
                points += 0.5

        # C_OLIM: New immigrant credits based on months since arrival
        if inputs.new_immigrant and inputs.date_of_aliyah:
            try:
                aliyah_date = datetime.strptime(
                    inputs.date_of_aliyah, "%Y-%m-%d")
                months_since_arrival = (
                    datetime.now() - aliyah_date).days // 30
                aliyah_year = aliyah_date.year

                # Different rules for pre-2022 and from 2022 onward
                if aliyah_year <= 2021:
                    # 42-month program
                    if months_since_arrival <= 18:
                        points += 3.0
                    elif months_since_arrival <= 30:
                        points += 2.0
                    elif months_since_arrival <= 42:
                        points += 1.0
                else:
                    # 54-month program (from 2022)
                    if months_since_arrival <= 12:
                        points += 1.0
                    elif months_since_arrival <= 30:
                        points += 3.0
                    elif months_since_arrival <= 42:
                        points += 2.0
                    elif months_since_arrival <= 54:
                        points += 1.0
            except (ValueError, TypeError):
                # Invalid date format, skip C_OLIM
                pass

        # C_SPOUSE_DEPENDENT: 1 or 0.5 points for dependent spouse
        if inputs.spouse_dependent and inputs.spouse:
            # Spouse must be resident, have no/low income, and meet dependency condition
            if inputs.spouse_income < 1000:  # Simplified: low income threshold
                points += 1.0  # 1 point for joint filing (simplified)

        # C_ALIMONY_EX_SPOUSE: 1 point for paying alimony
        if inputs.alimony_payment > 0:
            points += 1.0

        # C_CHILDREN: Complex calculation based on age and birth year
        if inputs.children > 0 and len(inputs.children_ages) > 0:
            for child_age in inputs.children_ages:
                # Standard rules (applicable to all unless special case)
                if child_age == 0:  # Birth year
                    points += 1.5
                elif 1 <= child_age <= 5:
                    # Check birth year for special rates (2017-2023 and 2024+)
                    # For now, use standard: 1 point per year, but enhanced for recent births
                    current_year = datetime.now().year
                    birth_year = current_year - child_age
                    if birth_year >= 2024:
                        # 2024+ births: age 1-2: 4.5, age 3: 3.5, age 4-5: 2.5
                        if child_age <= 2:
                            points += 4.5
                        elif child_age == 3:
                            points += 3.5
                        else:
                            points += 2.5
                    elif 2017 <= birth_year <= 2023:
                        # 2017-2023 births: ages 1-5: 2.5 points
                        points += 2.5
                    else:
                        # Standard: 1 point
                        points += 1.0
                elif 6 <= child_age <= 17:
                    # Per 2024 rule: 1 point per child (2 for single parent)
                    if inputs.is_single_parent:
                        points += 2.0
                    else:
                        points += 1.0
                elif child_age == 18:
                    points += 0.5

        # C_CHILDREN_SPECIAL_NEEDS: 2 points per qualifying disabled dependent
        if inputs.disabled_dependents > 0:
            points += inputs.disabled_dependents * 2.0

        # C_SINGLE_PARENT: 1 point per child (widow/widower or absent parent)
        if (inputs.is_single_parent or inputs.is_widow_widower) and inputs.children > 0:
            # This adds to regular child credits
            points += inputs.children * 1.0

        # C_CHILD_SUPPORT: 1 point total for child support
        if inputs.child_support_payment > 0:
            points += 1.0

        # C_EDUCATION: 1 point/year (BA, teaching) or 0.5 point/year (MA, PhD)
        # Maximum 3 years for BA/teaching, 2 years for MA/PhD
        if inputs.education_level and inputs.education_years_active > 0:
            education_lower = inputs.education_level.lower()
            if education_lower in ["ba", "bachelor", "teaching"]:
                years_to_count = min(inputs.education_years_active, 3)
                points += years_to_count * 1.0
            elif education_lower in ["ma", "master", "phd"]:
                years_to_count = min(inputs.education_years_active, 2)
                points += years_to_count * 0.5

        # C_PROFESSIONAL_TRAINING: 1 point per year, max 3 years
        if inputs.professional_training and inputs.education_years_active > 0:
            years_to_count = min(inputs.education_years_active, 3)
            points += years_to_count * 1.0

        return points

    @staticmethod
    def calculate_income_tax(annual_gross: float, credit_points: float) -> float:
        """
        Calculate income tax using annual progressive brackets.
        Income tax is calculated on annual gross AFTER deducting Bituach Leumi and pension.
        Credits are then subtracted from the calculated tax.
        """
        annual_tax = 0.0

        for bracket in TAX_BRACKETS:
            if annual_gross > bracket["min"]:
                taxable_in_bracket = min(
                    annual_gross, bracket["max"]) - bracket["min"]
                annual_tax += taxable_in_bracket * bracket["rate"]

        # Convert credit points to monthly monetary reduction
        # Using VALUE_POINT_MONTH (242 NIS) to reduce monthly tax
        monthly_tax = annual_tax / 12
        credit_reduction = credit_points * CREDIT_POINTS["value_point_month"]

        # Tax after credits (minimum 0)
        return max(0, monthly_tax - credit_reduction)

    @classmethod
    def calculate_net_salary(cls, inputs: CalculatorInputs) -> CalculationResult:
        """
        1. Pension deductions (employee)
        2. Bituach Leumi (National Insurance)
        3. Income tax
        4. Nikudot Zikuy (tax credits)
        5. City discount
        """
        monthly_salary = inputs.gross_salary
        annual_salary = monthly_salary * 12

        # Calculate credit points
        credit_points = cls.calculate_credit_points(inputs)

        # Step 1: Calculate pension deduction (employee portion)
        pension_employee = cls.calculate_pension_employee(
            monthly_salary, inputs.pension_rate)

        # Step 2: Calculate National Insurance (employee portion)
        national_insurance_employee = cls.calculate_national_insurance_employee(
            monthly_salary, is_self_employed=False
        )

        # Step 3: Calculate income tax on (gross - pension - NI)
        taxable_income = annual_salary - \
            (pension_employee * 12) - (national_insurance_employee * 12)
        income_tax = cls.calculate_income_tax(taxable_income, credit_points)

        # Health tax (standard calculation)
        health_tax = cls.calculate_health_tax(monthly_salary)

        # Employer contributions (informational, not deducted from employee)
        national_insurance_employer = cls.calculate_national_insurance_employer(
            monthly_salary)
        pension_employer = cls.calculate_pension_employer(monthly_salary)

        # Calculate total deductions (employee only)
        total_deductions = income_tax + \
            national_insurance_employee + health_tax + pension_employee
        net_salary = monthly_salary - total_deductions

        # Create tax breakdown with separated contributions
        tax_breakdown = TaxBreakdown(
            income_tax=income_tax,
            national_insurance_employee=national_insurance_employee,
            national_insurance_employer=national_insurance_employer,
            health_tax=health_tax,
            pension_employee=pension_employee,
            pension_employer=pension_employer,
            total_deductions=total_deductions
        )

        # Calculate effective tax rate (employee deductions only)
        effective_tax_rate = (
            total_deductions / monthly_salary * 100) if monthly_salary > 0 else 0

        # Convert credit points to monetary values
        tax_credit_annual = credit_points * CREDIT_POINTS["value_point_year"]
        tax_credit_monthly = credit_points * CREDIT_POINTS["value_point_month"]

        return CalculationResult(
            gross_salary=monthly_salary,
            net_salary=net_salary,
            tax_breakdown=tax_breakdown,
            credit_points=credit_points,
            tax_credit_annual=tax_credit_annual,
            tax_credit_monthly=tax_credit_monthly,
            effective_tax_rate=effective_tax_rate
        )
