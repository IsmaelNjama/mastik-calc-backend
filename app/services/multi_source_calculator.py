from app.models.calculator import CalculatorInputs, SelfEmploymentType
from app.services.tax_calculator import TaxCalculatorService
from app.utils.tax_constants import TAX_BRACKETS_MONTHLY, BITUACH_LEUMI, PENSION, CREDIT_POINTS, VAT

from typing import Tuple
from pydantic import BaseModel

VAT_RATE = VAT["rate"]  # 0.18


class EmployeeBreakdown(BaseModel):
    gross_month: float
    pension_employee_month: float
    bituach_leumi_employee_month: float
    health_tax_month: float
    income_tax_before_credits_month: float
    income_tax_after_credits_month: float
    credits_used_points: float
    net_month: float


class SelfEmployedVATBreakdown(BaseModel):
    revenue_incl_vat_year: float
    revenue_ex_vat_year: float
    vat_output_year: float
    vat_input_year: float
    vat_payable_year: float


class SelfEmployedBreakdown(BaseModel):
    profit_ex_vat_month: float
    pension_self_month: float
    bituach_leumi_self_month: float
    income_tax_before_credits_month: float
    income_tax_after_credits_month: float
    credits_used_points: float
    net_month_ex_vat: float
    net_month_cash: float
    vat: SelfEmployedVATBreakdown


class CombinedDetailedResult(BaseModel):
    credit_points_total: float
    credit_points_left_after_employee: float
    credit_points_left_after_self_employed: float

    employee: EmployeeBreakdown
    self_employed: SelfEmployedBreakdown

    gross_month_total: float
    net_month_total_cash: float

    income_tax_year_total: float
    bituach_leumi_year_total: float
    pension_year_total: float
    vat_payable_year_total: float
    total_deductions_year_total: float

    gross_year_total: float
    net_year_total_cash: float
    effective_tax_rate: float


class MultiSourceCalculatorService:
    @staticmethod
    def _round2(x: float) -> float:
        return round(float(x or 0.0), 2)

    @staticmethod
    def _split_vat(amount_incl_vat: float) -> Tuple[float, float]:
        amount_incl_vat = max(0.0, float(amount_incl_vat))
        amount_ex_vat = amount_incl_vat / (1.0 + VAT_RATE)
        vat_amount = amount_incl_vat - amount_ex_vat
        return MultiSourceCalculatorService._round2(amount_ex_vat), MultiSourceCalculatorService._round2(vat_amount)

    @staticmethod
    def _calc_progressive_tax_monthly(monthly_taxable: float) -> float:
        salary = max(0.0, float(monthly_taxable))
        tax = 0.0
        for bracket in TAX_BRACKETS_MONTHLY:
            bmin = float(bracket["min"])
            bmax = float(bracket["max"])
            rate = float(bracket["rate"])
            if salary > bmin:
                base = min(salary, bmax) - bmin
                if base > 0:
                    tax += base * rate
        return MultiSourceCalculatorService._round2(tax)

    @staticmethod
    def _apply_credits_to_tax(tax_before: float, points_available: float) -> Tuple[float, float, float]:
        """
        Returns:
          tax_after, points_remaining, points_used
        """
        credit_value = float(CREDIT_POINTS["POINT_VALUE_MONTH"])
        tax_before = max(0.0, float(tax_before))
        points_available = max(0.0, float(points_available))

        if tax_before == 0.0 or points_available == 0.0:
            return MultiSourceCalculatorService._round2(tax_before), MultiSourceCalculatorService._round2(points_available), 0.0

        max_reduction = points_available * credit_value

        if max_reduction >= tax_before:
            points_used = tax_before / credit_value
            points_remaining = points_available - points_used
            return 0.0, MultiSourceCalculatorService._round2(points_remaining), MultiSourceCalculatorService._round2(points_used)

        tax_after = tax_before - max_reduction
        return MultiSourceCalculatorService._round2(tax_after), 0.0, MultiSourceCalculatorService._round2(points_available)

    @staticmethod
    def _calc_bituach_by_tiers(amount_month: float, tiers: list) -> float:
        amount = max(0.0, float(amount_month))
        total = 0.0
        for t in tiers:
            tmin = float(t["min"])
            tmax = float(t["max"])
            rate = float(t["rate"])
            if amount > tmin:
                base = min(amount, tmax) - tmin
                if base > 0:
                    total += base * rate
        return MultiSourceCalculatorService._round2(total)

    @staticmethod
    def _calc_pension_self_employed(monthly_income: float) -> float:
        income = max(0.0, float(monthly_income))
        cfg = PENSION["self_employed"]

        mandatory_over = float(cfg["mandatory_if_income_over"])
        if income <= mandatory_over:
            return 0.0

        threshold = float(cfg["threshold"])
        below = min(income, threshold)
        above = max(0.0, income - threshold)

        pension = below * float(cfg["rate_below_threshold"]) + above * float(cfg["rate_above_threshold_max"])
        return MultiSourceCalculatorService._round2(pension)

    @staticmethod
    def calculate_combined_employment_detailed(inputs: CalculatorInputs) -> CombinedDetailedResult:
        credit_points_total = TaxCalculatorService.calculate_credit_points(inputs)

        # Employee part
        employee_gross = float(inputs.gross_salary)

        pension_employee = TaxCalculatorService.calculate_pension_employee(
            employee_gross, getattr(inputs, "pension_rate", None)
        )
        bituach_employee = MultiSourceCalculatorService._calc_bituach_by_tiers(
            employee_gross, BITUACH_LEUMI["employee"]
        )
        health_tax = 0.0

        employee_taxable_base = max(0.0, employee_gross - pension_employee - bituach_employee)
        employee_income_tax_before = MultiSourceCalculatorService._calc_progressive_tax_monthly(employee_taxable_base)

        employee_income_tax_after, points_left_after_employee, points_used_employee = MultiSourceCalculatorService._apply_credits_to_tax(
            employee_income_tax_before, credit_points_total
        )

        employee_total_ded = MultiSourceCalculatorService._round2(
            employee_income_tax_after + pension_employee + bituach_employee + health_tax
        )
        employee_net = MultiSourceCalculatorService._round2(employee_gross - employee_total_ded)

        employee_breakdown = EmployeeBreakdown(
            gross_month=MultiSourceCalculatorService._round2(employee_gross),
            pension_employee_month=pension_employee,
            bituach_leumi_employee_month=bituach_employee,
            health_tax_month=health_tax,
            income_tax_before_credits_month=employee_income_tax_before,
            income_tax_after_credits_month=employee_income_tax_after,
            credits_used_points=points_used_employee,
            net_month=employee_net,
        )

        # Self-employed part
        if inputs.self_employed_income:
            se = inputs.self_employed_income

            revenue_incl_vat_year = float(se.revenue)
            if se.actual_expenses and se.actual_expenses > 0:
                expenses_incl_vat_year = float(se.actual_expenses)
            else:
                expenses_incl_vat_year = revenue_incl_vat_year * (float(se.expense_rate) / 100.0)

            if se.type == SelfEmploymentType.ESEK_MURSHE:
                revenue_ex_vat_year, vat_output_year = MultiSourceCalculatorService._split_vat(revenue_incl_vat_year)
                expenses_ex_vat_year, vat_input_year = MultiSourceCalculatorService._split_vat(expenses_incl_vat_year)
                vat_payable_year = MultiSourceCalculatorService._round2(max(0.0, vat_output_year - vat_input_year))
            else:
                revenue_ex_vat_year = MultiSourceCalculatorService._round2(revenue_incl_vat_year)
                expenses_ex_vat_year = MultiSourceCalculatorService._round2(expenses_incl_vat_year)
                vat_output_year = 0.0
                vat_input_year = 0.0
                vat_payable_year = 0.0

            profit_ex_vat_year = MultiSourceCalculatorService._round2(max(0.0, revenue_ex_vat_year - expenses_ex_vat_year))
            profit_ex_vat_month = profit_ex_vat_year / 12.0

            pension_self = MultiSourceCalculatorService._calc_pension_self_employed(profit_ex_vat_month)
            bituach_self = MultiSourceCalculatorService._calc_bituach_by_tiers(
                profit_ex_vat_month, BITUACH_LEUMI["self_employed"]
            )

            se_taxable_base = max(0.0, profit_ex_vat_month - pension_self - bituach_self)
            se_income_tax_before = MultiSourceCalculatorService._calc_progressive_tax_monthly(se_taxable_base)

            se_income_tax_after, points_left_after_se, points_used_se = MultiSourceCalculatorService._apply_credits_to_tax(
                se_income_tax_before, points_left_after_employee
            )

            se_total_ded_month = MultiSourceCalculatorService._round2(se_income_tax_after + pension_self + bituach_self)
            se_net_month_ex_vat = MultiSourceCalculatorService._round2(profit_ex_vat_month - se_total_ded_month)

            vat_payable_month = MultiSourceCalculatorService._round2(vat_payable_year / 12.0)
            se_net_month_cash = MultiSourceCalculatorService._round2(se_net_month_ex_vat - vat_payable_month)

            se_vat_breakdown = SelfEmployedVATBreakdown(
                revenue_incl_vat_year=MultiSourceCalculatorService._round2(revenue_incl_vat_year),
                revenue_ex_vat_year=MultiSourceCalculatorService._round2(revenue_ex_vat_year),
                vat_output_year=MultiSourceCalculatorService._round2(vat_output_year),
                vat_input_year=MultiSourceCalculatorService._round2(vat_input_year),
                vat_payable_year=MultiSourceCalculatorService._round2(vat_payable_year),
            )

            self_breakdown = SelfEmployedBreakdown(
                profit_ex_vat_month=MultiSourceCalculatorService._round2(profit_ex_vat_month),
                pension_self_month=pension_self,
                bituach_leumi_self_month=bituach_self,
                income_tax_before_credits_month=se_income_tax_before,
                income_tax_after_credits_month=se_income_tax_after,
                credits_used_points=points_used_se,
                net_month_ex_vat=se_net_month_ex_vat,
                net_month_cash=se_net_month_cash,
                vat=se_vat_breakdown,
            )
        else:
            points_left_after_se = points_left_after_employee
            self_breakdown = SelfEmployedBreakdown(
                profit_ex_vat_month=0.0,
                pension_self_month=0.0,
                bituach_leumi_self_month=0.0,
                income_tax_before_credits_month=0.0,
                income_tax_after_credits_month=0.0,
                credits_used_points=0.0,
                net_month_ex_vat=0.0,
                net_month_cash=0.0,
                vat=SelfEmployedVATBreakdown(
                    revenue_incl_vat_year=0.0,
                    revenue_ex_vat_year=0.0,
                    vat_output_year=0.0,
                    vat_input_year=0.0,
                    vat_payable_year=0.0,
                ),
            )

        gross_month_total = MultiSourceCalculatorService._round2(
            employee_breakdown.gross_month + self_breakdown.profit_ex_vat_month
        )
        net_month_total_cash = MultiSourceCalculatorService._round2(
            employee_breakdown.net_month + self_breakdown.net_month_cash
        )

        income_tax_year_total = MultiSourceCalculatorService._round2(
            (employee_breakdown.income_tax_after_credits_month + self_breakdown.income_tax_after_credits_month) * 12.0
        )
        bituach_year_total = MultiSourceCalculatorService._round2(
            (employee_breakdown.bituach_leumi_employee_month + self_breakdown.bituach_leumi_self_month) * 12.0
        )
        pension_year_total = MultiSourceCalculatorService._round2(
            (employee_breakdown.pension_employee_month + self_breakdown.pension_self_month) * 12.0
        )
        vat_payable_year_total = self_breakdown.vat.vat_payable_year

        total_deductions_year_total = MultiSourceCalculatorService._round2(
            (
                employee_breakdown.income_tax_after_credits_month
                + employee_breakdown.bituach_leumi_employee_month
                + employee_breakdown.health_tax_month
                + employee_breakdown.pension_employee_month
                + self_breakdown.income_tax_after_credits_month
                + self_breakdown.bituach_leumi_self_month
                + self_breakdown.pension_self_month
            ) * 12.0
        )

        gross_year_total = MultiSourceCalculatorService._round2(gross_month_total * 12.0)
        net_year_total_cash = MultiSourceCalculatorService._round2(net_month_total_cash * 12.0)

        effective_tax_rate = (
            MultiSourceCalculatorService._round2((total_deductions_year_total / gross_year_total) * 100.0)
            if gross_year_total > 0
            else 0.0
        )

        return CombinedDetailedResult(
            credit_points_total=MultiSourceCalculatorService._round2(credit_points_total),
            credit_points_left_after_employee=MultiSourceCalculatorService._round2(points_left_after_employee),
            credit_points_left_after_self_employed=MultiSourceCalculatorService._round2(points_left_after_se),

            employee=employee_breakdown,
            self_employed=self_breakdown,

            gross_month_total=gross_month_total,
            net_month_total_cash=net_month_total_cash,

            income_tax_year_total=income_tax_year_total,
            bituach_leumi_year_total=bituach_year_total,
            pension_year_total=pension_year_total,
            vat_payable_year_total=vat_payable_year_total,
            total_deductions_year_total=total_deductions_year_total,

            gross_year_total=gross_year_total,
            net_year_total_cash=net_year_total_cash,
            effective_tax_rate=effective_tax_rate,
        )
