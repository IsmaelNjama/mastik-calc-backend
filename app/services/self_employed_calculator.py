from app.models.calculator import (
    CalculatorInputs,
    CalculationResult,
    SelfEmploymentType,
    TaxBreakdown,
)
from app.services.tax_calculator import TaxCalculatorService
from app.utils.tax_constants import (
    TAX_BRACKETS_MONTHLY,
    BITUACH_LEUMI,
    PENSION,
    CREDIT_POINTS,
    VAT,
)

VAT_RATE = VAT["rate"]  # 0.18


class SelfEmployedCalculatorService:
    @staticmethod
    def _round2(x: float) -> float:
        return round(float(x or 0.0), 2)

    @staticmethod
    def _split_vat(amount_incl_vat: float) -> tuple[float, float]:
        """
        Split VAT-included amount into (amount_ex_vat, vat_amount)
        """
        amount_incl_vat = max(0.0, float(amount_incl_vat))
        amount_ex_vat = amount_incl_vat / (1.0 + VAT_RATE)
        vat_amount = amount_incl_vat - amount_ex_vat
        return (
            SelfEmployedCalculatorService._round2(amount_ex_vat),
            SelfEmployedCalculatorService._round2(vat_amount),
        )

    @staticmethod
    def _calc_income_tax_monthly(monthly_taxable: float) -> float:
        tax = 0.0
        salary = max(0.0, float(monthly_taxable))

        for bracket in TAX_BRACKETS_MONTHLY:
            bmin = bracket["min"]
            bmax = bracket["max"]
            rate = bracket["rate"]

            if salary > bmin:
                base = min(salary, bmax) - bmin
                if base > 0:
                    tax += base * rate

        return SelfEmployedCalculatorService._round2(tax)

    @staticmethod
    def calculate_bituach_leumi_self_employed(monthly_income: float) -> float:
        income = max(0.0, float(monthly_income))
        total = 0.0

        for tier in BITUACH_LEUMI["self_employed"]:
            tmin = tier["min"]
            tmax = tier["max"]
            rate = tier["rate"]

            if income > tmin:
                base = min(income, tmax) - tmin
                if base > 0:
                    total += base * rate

        return SelfEmployedCalculatorService._round2(total)

    @staticmethod
    def calculate_pension_self_employed(monthly_income: float) -> float:
        income = max(0.0, float(monthly_income))
        cfg = PENSION["self_employed"]

        if income <= cfg["mandatory_if_income_over"]:
            return 0.0

        below = min(income, cfg["threshold"])
        above = max(0.0, income - cfg["threshold"])

        pension = (
            below * cfg["rate_below_threshold"]
            + above * cfg["rate_above_threshold_max"]
        )

        return SelfEmployedCalculatorService._round2(pension)

    @staticmethod
    def calculate_self_employed_income(inputs: CalculatorInputs) -> CalculationResult:
        if not inputs.self_employed_income:
            raise ValueError("Self-employed income data is required")

        se = inputs.self_employed_income

        # ===== 1. Annual revenue and expenses (INPUT IS VAT INCLUDED) =====

        revenue_incl_vat_year = float(se.revenue)

        if se.actual_expenses and se.actual_expenses > 0:
            expenses_incl_vat_year = float(se.actual_expenses)
        else:
            expenses_incl_vat_year = revenue_incl_vat_year * (se.expense_rate / 100)

        # ===== 2. VAT handling =====

        if se.type == SelfEmploymentType.ESEK_MURSHE:
            revenue_ex_vat_year, vat_output_year = SelfEmployedCalculatorService._split_vat(
                revenue_incl_vat_year
            )
            expenses_ex_vat_year, vat_input_year = SelfEmployedCalculatorService._split_vat(
                expenses_incl_vat_year
            )
            vat_payable_year = max(0.0, vat_output_year - vat_input_year)
        else:
            # ESEK PATUR
            revenue_ex_vat_year = revenue_incl_vat_year
            expenses_ex_vat_year = expenses_incl_vat_year
            vat_output_year = 0.0
            vat_input_year = 0.0
            vat_payable_year = 0.0

        revenue_ex_vat_year = SelfEmployedCalculatorService._round2(revenue_ex_vat_year)
        expenses_ex_vat_year = SelfEmployedCalculatorService._round2(expenses_ex_vat_year)
        vat_payable_year = SelfEmployedCalculatorService._round2(vat_payable_year)

        # ===== 3. Net business income (EX VAT) =====

        net_business_income_year = max(
            0.0, revenue_ex_vat_year - expenses_ex_vat_year
        )
        net_business_income_year = SelfEmployedCalculatorService._round2(
            net_business_income_year
        )

        monthly_income_ex_vat = net_business_income_year / 12.0

        # ===== 4. Credit points =====

        credit_points = TaxCalculatorService.calculate_credit_points(inputs)

        # ===== 5. Monthly taxes =====

        pension_month = SelfEmployedCalculatorService.calculate_pension_self_employed(
            monthly_income_ex_vat
        )
        bituach_month = SelfEmployedCalculatorService.calculate_bituach_leumi_self_employed(
            monthly_income_ex_vat
        )

        taxable_base = max(
            0.0, monthly_income_ex_vat - pension_month - bituach_month
        )

        income_tax_before_credits = SelfEmployedCalculatorService._calc_income_tax_monthly(
            taxable_base
        )

        credit_reduction = credit_points * CREDIT_POINTS["POINT_VALUE_MONTH"]
        income_tax_month = max(0.0, income_tax_before_credits - credit_reduction)
        income_tax_month = SelfEmployedCalculatorService._round2(income_tax_month)

        total_deductions_month = (
            income_tax_month + pension_month + bituach_month
        )
        total_deductions_month = SelfEmployedCalculatorService._round2(
            total_deductions_month
        )

        net_month_ex_vat = SelfEmployedCalculatorService._round2(
            monthly_income_ex_vat - total_deductions_month
        )

        # ===== 6. Annualisation =====

        income_tax_year = SelfEmployedCalculatorService._round2(income_tax_month * 12)
        pension_year = SelfEmployedCalculatorService._round2(pension_month * 12)
        bituach_year = SelfEmployedCalculatorService._round2(bituach_month * 12)
        total_deductions_year = SelfEmployedCalculatorService._round2(
            total_deductions_month * 12
        )

        net_year_ex_vat = SelfEmployedCalculatorService._round2(net_month_ex_vat * 12)
        net_year_cash = SelfEmployedCalculatorService._round2(
            net_year_ex_vat - vat_payable_year
        )

        # ===== 7. Breakdown =====

        tax_breakdown = TaxBreakdown(
            income_tax=income_tax_year,
            national_insurance=bituach_year,
            health_tax=0.0,
            pension_employee=pension_year,
            total_deductions=total_deductions_year,
            vat_output=vat_output_year,
            vat_input=vat_input_year,
            vat_payable=vat_payable_year,
            revenue_incl_vat=revenue_incl_vat_year,
            revenue_ex_vat=revenue_ex_vat_year,
        )

        effective_tax_rate = (
            (total_deductions_year / net_business_income_year) * 100
            if net_business_income_year > 0
            else 0.0
        )

        return CalculationResult(
            gross_salary=net_business_income_year,
            net_salary=net_year_cash,
            tax_breakdown=tax_breakdown,
            credit_points=credit_points,
            effective_tax_rate=SelfEmployedCalculatorService._round2(effective_tax_rate),
        )
