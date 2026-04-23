"""NSVIF-inspired Z3 constraint definitions for data quality verification.

Implements the three-agent pattern from arXiv:2601.17789:
  1. Formulation: Data quality rules -> Z3 constraints
  2. Checking: Logic constraints -> Python code; Semantic -> LLM
  3. Solver: Z3 evaluates composite formula -> SAT/UNSAT + violation report
"""

from __future__ import annotations

from dataclasses import dataclass, field

from z3 import And, Bool, If, Int, Not, Or, Solver, sat

from interior_minister.schemas import DEPARTMENTS, DATASET_SCHEMAS


@dataclass
class ConstraintResult:
    """Result of a constraint satisfaction check."""

    dataset: str
    satisfied: bool
    total_constraints: int
    violations: list[str] = field(default_factory=list)

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    def summary(self) -> str:
        status = "SAT" if self.satisfied else "UNSAT"
        return (
            f"[{status}] {self.dataset}: "
            f"{self.total_constraints - self.violation_count}/{self.total_constraints} constraints satisfied"
        )


def check_department_constraints(
    departments: list[str | int],
    dataset: str,
) -> ConstraintResult:
    """Verify all department values are valid (1-19 or known names)."""
    valid_codes = set(DEPARTMENTS.keys())
    valid_names = {d.upper() for d in DEPARTMENTS.values()}

    violations = []
    for i, dept in enumerate(departments):
        if isinstance(dept, int):
            if dept not in valid_codes:
                violations.append(f"Row {i}: department code {dept} not in 1..19")
        elif isinstance(dept, str):
            if dept.upper() not in valid_names and not dept.isdigit():
                violations.append(f"Row {i}: department '{dept}' not recognized")
            elif dept.isdigit() and int(dept) not in valid_codes:
                violations.append(f"Row {i}: department code {dept} not in 1..19")

    return ConstraintResult(
        dataset=dataset,
        satisfied=len(violations) == 0,
        total_constraints=len(departments),
        violations=violations[:50],
    )


def check_year_constraints(
    years: list[int],
    dataset: str,
) -> ConstraintResult:
    """Verify all year values fall within the valid range for the dataset."""
    schema = DATASET_SCHEMAS.get(dataset)
    if schema is None:
        return ConstraintResult(dataset=dataset, satisfied=True, total_constraints=0)

    lo, hi = schema["time_range"]
    violations = []
    for i, year in enumerate(years):
        if not (lo <= year <= hi):
            violations.append(f"Row {i}: year {year} outside [{lo}, {hi}]")

    return ConstraintResult(
        dataset=dataset,
        satisfied=len(violations) == 0,
        total_constraints=len(years),
        violations=violations[:50],
    )


def check_non_negative(
    values: list[int | float],
    column_name: str,
    dataset: str,
) -> ConstraintResult:
    """Verify all values in a count column are non-negative."""
    violations = []
    for i, val in enumerate(values):
        if val < 0:
            violations.append(f"Row {i}: {column_name} = {val} (negative)")

    return ConstraintResult(
        dataset=dataset,
        satisfied=len(violations) == 0,
        total_constraints=len(values),
        violations=violations[:50],
    )


def check_sex_values(
    values: list[str],
    dataset: str,
) -> ConstraintResult:
    """Verify sex/gender column contains only valid values."""
    valid = {"M", "F", "MASCULINO", "FEMENINO", "MASCULINO ", "FEMENINO "}
    violations = []
    for i, val in enumerate(values):
        if val.strip().upper() not in valid:
            violations.append(f"Row {i}: sex value '{val}' not recognized")

    return ConstraintResult(
        dataset=dataset,
        satisfied=len(violations) == 0,
        total_constraints=len(values),
        violations=violations[:50],
    )


def build_z3_schema_formula(
    dataset: str,
    row_count: int,
    has_valid_departments: bool,
    has_valid_years: bool,
    has_non_negative_counts: bool,
    has_valid_sex: bool | None = None,
) -> tuple[bool, list[str]]:
    """Build a Z3 formula for composite schema validation.

    Returns (satisfied, list_of_unsat_constraints).
    """
    solver = Solver()

    dept_ok = Bool("departments_valid")
    year_ok = Bool("years_valid")
    count_ok = Bool("counts_non_negative")
    row_exists = Bool("has_rows")

    solver.add(dept_ok == has_valid_departments)
    solver.add(year_ok == has_valid_years)
    solver.add(count_ok == has_non_negative_counts)
    solver.add(row_exists == (row_count > 0))

    requirements = [dept_ok, year_ok, count_ok, row_exists]

    if has_valid_sex is not None:
        sex_ok = Bool("sex_values_valid")
        solver.add(sex_ok == has_valid_sex)
        requirements.append(sex_ok)

    solver.add(And(*requirements))

    if solver.check() == sat:
        return True, []

    unsat = []
    if not has_valid_departments:
        unsat.append("departments_valid")
    if not has_valid_years:
        unsat.append("years_valid")
    if not has_non_negative_counts:
        unsat.append("counts_non_negative")
    if row_count == 0:
        unsat.append("has_rows")
    if has_valid_sex is not None and not has_valid_sex:
        unsat.append("sex_values_valid")

    return False, unsat


def check_cross_dataset_dv_subset(
    delitos_dv_count: int,
    vd_count: int,
    year: int,
) -> ConstraintResult:
    """Verify DV reports in delitos_denunciados are consistent with violencia_domestica dataset."""
    violations = []
    if vd_count > delitos_dv_count * 1.5:
        violations.append(
            f"Year {year}: VD dataset ({vd_count}) has >50% more records "
            f"than DV subset in delitos ({delitos_dv_count})"
        )

    return ConstraintResult(
        dataset="cross_dataset_dv",
        satisfied=len(violations) == 0,
        total_constraints=1,
        violations=violations,
    )
