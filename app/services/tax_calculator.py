from app.models.calculator import CalculatorInputs, CalculationResult, TaxBreakdown
from app.utils.tax_constants import (
    TAX_BRACKETS_MONTHLY,
    BITUACH_LEUMI,
    PENSION,
    CREDIT_POINTS,
    CHILD_CREDIT_RULES,
)

class TaxCalculatorService:
    @staticmethod
    def _round2(x: float) -> float:
        return round(float(x or 0.0), 2)

    @staticmethod
    def calculate_income_tax(monthly_salary: float, credit_points: float) -> float:
        """
        Monthly income tax using monthly brackets, then subtract credit points value.
        """
        salary = max(0.0, float(monthly_salary))
        tax = 0.0

        for bracket in TAX_BRACKETS_MONTHLY:
            bmin = float(bracket["min"])
            bmax = float(bracket["max"])
            rate = float(bracket["rate"])

            if salary > bmin:
                taxable_in_bracket = min(salary, bmax) - bmin
                if taxable_in_bracket > 0:
                    tax += taxable_in_bracket * rate

        credit_reduction = float(credit_points) * float(CREDIT_POINTS["POINT_VALUE_MONTH"])
        tax_after_credits = max(0.0, tax - credit_reduction)

        return TaxCalculatorService._round2(tax_after_credits)

    @staticmethod
    def calculate_bituach_leumi_employee(monthly_salary: float) -> float:
        """
        Employee Bituach Leumi using tier rules from BITUACH_LEUMI["employee"].
        """
        salary = max(0.0, float(monthly_salary))
        tiers = BITUACH_LEUMI["employee"]

        total = 0.0
        for t in tiers:
            tmin, tmax, rate = float(t["min"]), float(t["max"]), float(t["rate"])
            if salary > tmin:
                base = min(salary, tmax) - tmin
                if base > 0:
                    total += base * rate

        return TaxCalculatorService._round2(total)

    @staticmethod
    def calculate_health_tax(monthly_salary: float) -> float:
        """
        There is no separate HEALTH_TAX block in the current constants file.
        To avoid using unverified rates, this method returns 0.
        """
        return 0.0

    @staticmethod
    def calculate_pension_employee(monthly_salary: float, pension_rate_percent: float | None) -> float:
        """
        Employee pension contribution.
        The minimum enforced rate is PENSION["employee_rate"].
        If UI provides a rate, enforce the minimum anyway.
        """
        salary = max(0.0, float(monthly_salary))
        min_rate = float(PENSION["employee_rate"])

        if pension_rate_percent is None:
            rate = min_rate
        else:
            rate = max(float(pension_rate_percent) / 100.0, min_rate)

        return TaxCalculatorService._round2(salary * rate)

    @staticmethod
    def _child_points_for_parent(child: dict, parent_role: str, is_single_parent: bool) -> float:
        """
        parent_role: "mother" or "father"
        child fields expected:
          - age: int
          - special_needs: bool (optional)
          - mother_waives_to_father: bool (optional)
          - transfer_fraction_to_father: float 0..1 (optional, for partial transfer)
          - lives_with_parent: bool (optional, for single-parent extra)
        """
        points = 0.0

        # Special needs child credit
        if child.get("special_needs"):
            points += float(CHILD_CREDIT_RULES["SPECIAL_NEEDS_CHILD"]["points_per_child"])

        age = child.get("age")
        if age is None:
            raise ValueError("Each child in children_details must include age")

        age = int(age)

        # Default holder rule (typically "mother")
        default_holder = CHILD_CREDIT_RULES["TRANSFER_RULES"]["default_holder"]
        holder = default_holder

        # Transfer to father if mother waives (if allowed by rules)
        if child.get("mother_waives_to_father") and CHILD_CREDIT_RULES["TRANSFER_RULES"]["father_possible_if_mother_waives"]:
            holder = "father"

        # Apply age-based rules
        def add_if_applicable(rule_key: str):
            nonlocal points
            rule = CHILD_CREDIT_RULES[rule_key]
            if int(rule["min_age"]) <= age <= int(rule["max_age"]):
                # "dependent_parent" means credits apply to the eligible parent per rules
                if holder == rule["granted_to"] or (rule["granted_to"] == "dependent_parent"):
                    points += float(rule["points_per_child"])

        add_if_applicable("AGE_0_5")
        add_if_applicable("AGE_6_17")
        add_if_applicable("AGE_18")

        # Single parent extra: apply only if the child lives with the parent
        if is_single_parent:
            if child.get("lives_with_parent") and "SINGLE_PARENT_EXTRA" in CHILD_CREDIT_RULES:
                points += float(CHILD_CREDIT_RULES["SINGLE_PARENT_EXTRA"]["points_per_child"])

        # Partial transfer: split points between mother/father by fraction (if enabled)
        if (
            CHILD_CREDIT_RULES["TRANSFER_RULES"].get("partial_transfer_allowed")
            and child.get("transfer_fraction_to_father") is not None
        ):
            frac = float(child["transfer_fraction_to_father"])
            frac = max(0.0, min(1.0, frac))
            if parent_role == "father":
                points = points * frac
            elif parent_role == "mother":
                points = points * (1.0 - frac)

        # Return points only for the requested parent if they are the holder
        return points if parent_role == holder or holder == "dependent_parent" else 0.0

    @staticmethod
    def calculate_credit_points(inputs: CalculatorInputs) -> float:
        """
        Calculates total credit points.
        This implementation only adds points when it has enough data to do so deterministically.
        """
        points = 0.0

        # Israeli resident base credits
        if getattr(inputs, "is_resident", True):
            points += float(CREDIT_POINTS["C_RESIDENT"])

        # Woman extra credits
        gender = getattr(inputs, "gender", None)
        if gender in ("female", "F", "woman"):
            points += float(CREDIT_POINTS["C_WOMAN"])

        # Dependent spouse credits (only if filing mode is explicitly provided)
        spouse = getattr(inputs, "spouse", False)
        if spouse:
            filing_mode = getattr(inputs, "filing_mode", None)  # "joint_filing" or "separate_filing"
            if filing_mode in ("joint_filing", "separate_filing"):
                points += float(CREDIT_POINTS["C_DEPENDENT_SPOUSE"][filing_mode])

        # Foreign worker credits (only if explicitly provided)
        foreign_worker_type = getattr(inputs, "foreign_worker_type", None)  # "caregiver" or "other"
        if foreign_worker_type in ("caregiver", "other"):
            points += float(CREDIT_POINTS["C_FOREIGN_WORKER"][foreign_worker_type])
            if gender in ("female", "F", "woman"):
                points += float(CREDIT_POINTS["C_FOREIGN_WORKER"]["female_extra"])

        # Children credits (requires full details for correct allocation)
        children_details = getattr(inputs, "children_details", None)
        children_count = getattr(inputs, "children", 0)

        if children_details is None:
            if children_count:
                raise ValueError("children_details is required to calculate child credit points correctly")
        else:
            parent_role = getattr(inputs, "parent_role", None)  # "mother" or "father"
            if parent_role not in ("mother", "father"):
                raise ValueError("parent_role must be provided as 'mother' or 'father' to allocate child credits")
            is_single_parent = bool(getattr(inputs, "is_single_parent", False))

            for child in children_details:
                points += TaxCalculatorService._child_points_for_parent(child, parent_role, is_single_parent)

        return TaxCalculatorService._round2(points)

    @classmethod
    def _calc_employee_source(cls, gross_salary: float, credit_points_for_this_job: float, pension_rate: float | None) -> dict:
        """
        Calculate all payroll deductions for a single employment source (one employer).
        Credit points are applied only if passed in credit_points_for_this_job.
        """
        gross_salary = float(gross_salary)

        pension_employee = cls.calculate_pension_employee(gross_salary, pension_rate)
        bituach_leumi = cls.calculate_bituach_leumi_employee(gross_salary)
        health_tax = cls.calculate_health_tax(gross_salary)

        income_tax = cls.calculate_income_tax(gross_salary, credit_points_for_this_job)

        total_deductions = cls._round2(income_tax + bituach_leumi + health_tax + pension_employee)
        net_salary = cls._round2(gross_salary - total_deductions)

        breakdown = TaxBreakdown(
            income_tax=income_tax,
            national_insurance=bituach_leumi,
            health_tax=health_tax,
            pension_employee=pension_employee,
            total_deductions=total_deductions,
        )

        effective_tax_rate = cls._round2((total_deductions / gross_salary * 100.0) if gross_salary > 0 else 0.0)

        return {
            "gross_salary": gross_salary,
            "net_salary": net_salary,
            "tax_breakdown": breakdown,
            "effective_tax_rate": effective_tax_rate,
        }

    @classmethod
    def calculate_net_salary(cls, inputs: CalculatorInputs) -> CalculationResult:
        credit_points_total = cls.calculate_credit_points(inputs)
        pension_rate = getattr(inputs, "pension_rate", None)

        employers = getattr(inputs, "employers", None)

        # Case 1: single employer (backward compatible with existing UI)
        if not employers:
            gross_salary = float(inputs.gross_salary)

            r = cls._calc_employee_source(
                gross_salary=gross_salary,
                credit_points_for_this_job=credit_points_total,
                pension_rate=pension_rate,
            )

            return CalculationResult(
                gross_salary=r["gross_salary"],
                net_salary=r["net_salary"],
                tax_breakdown=r["tax_breakdown"],
                credit_points=cls._round2(credit_points_total),
                effective_tax_rate=r["effective_tax_rate"],
            )

        # Case 2: exactly two employers (two jobs, employee-only scenario)
        if len(employers) != 2:
            raise ValueError("For employee-only scenario with multiple jobs, employers must contain exactly 2 items")

        job1 = employers[0]
        job2 = employers[1]

        is_primary_1 = bool(job1.get("is_primary", True))
        is_primary_2 = bool(job2.get("is_primary", False))

        # Exactly one employer must be marked as primary (credit points applied there)
        if is_primary_1 == is_primary_2:
            raise ValueError("Exactly one employer must be marked as primary (is_primary=True)")

        cp_job1 = credit_points_total if is_primary_1 else 0.0
        cp_job2 = credit_points_total if is_primary_2 else 0.0

        r1 = cls._calc_employee_source(
            gross_salary=float(job1["gross_salary"]),
            credit_points_for_this_job=cp_job1,
            pension_rate=pension_rate,
        )
        r2 = cls._calc_employee_source(
            gross_salary=float(job2["gross_salary"]),
            credit_points_for_this_job=cp_job2,
            pension_rate=pension_rate,
        )

        gross_total = cls._round2(r1["gross_salary"] + r2["gross_salary"])
        net_total = cls._round2(r1["net_salary"] + r2["net_salary"])

        income_tax_total = cls._round2(r1["tax_breakdown"].income_tax + r2["tax_breakdown"].income_tax)
        ni_total = cls._round2(r1["tax_breakdown"].national_insurance + r2["tax_breakdown"].national_insurance)
        health_total = cls._round2(r1["tax_breakdown"].health_tax + r2["tax_breakdown"].health_tax)
        pension_total = cls._round2(r1["tax_breakdown"].pension_employee + r2["tax_breakdown"].pension_employee)
        deductions_total = cls._round2(r1["tax_breakdown"].total_deductions + r2["tax_breakdown"].total_deductions)

        combined_breakdown = TaxBreakdown(
            income_tax=income_tax_total,
            national_insurance=ni_total,
            health_tax=health_total,
            pension_employee=pension_total,
            total_deductions=deductions_total,
        )

        effective_tax_rate_total = cls._round2((deductions_total / gross_total * 100.0) if gross_total > 0 else 0.0)

        result = CalculationResult(
            gross_salary=gross_total,
            net_salary=net_total,
            tax_breakdown=combined_breakdown,
            credit_points=cls._round2(credit_points_total),
            effective_tax_rate=effective_tax_rate_total,
        )

        # IMPORTANT: If CalculationResult does not have a "sources" field,
        # either add it to the model or attach dynamically (as done here).
        # The UI can then show per-employer breakdown + which employer used credit points.
        setattr(result, "sources", [
            {
                "source_type": "employer",
                "source_id": str(job1.get("id", "job1")),
                "is_primary": is_primary_1,
                "credit_points_applied": cls._round2(cp_job1),
                **r1,
            },
            {
                "source_type": "employer",
                "source_id": str(job2.get("id", "job2")),
                "is_primary": is_primary_2,
                "credit_points_applied": cls._round2(cp_job2),
                **r2,
            },
        ])

        return result
