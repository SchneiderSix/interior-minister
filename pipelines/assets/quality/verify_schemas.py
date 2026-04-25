""" @bruin
name: quality.verify_schemas
type: python
tags:
  - quality
depends:
  - transformation.upload_gcs
description: Per-dataset schema validation using Z3 constraints
@bruin """

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

# Allow imports from the project src/ tree.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from interior_minister.constraints import (
    ConstraintResult,
    build_z3_schema_formula,
    check_department_constraints,
    check_non_negative,
    check_sex_values,
    check_year_constraints,
)
from interior_minister.schemas import DATASET_SCHEMAS

PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "tabular"


def _find_column(df: pl.DataFrame, candidates: list[str]) -> str | None:
    """Return the first column name from *candidates* that exists in *df*."""
    lower_map = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def _validate_dataset(path: Path) -> list[ConstraintResult]:
    """Run all applicable constraint checks on a single parquet file."""
    dataset_name = path.stem
    df = pl.read_parquet(path)
    results: list[ConstraintResult] = []

    if len(df) == 0:
        results.append(
            ConstraintResult(
                dataset=dataset_name,
                satisfied=False,
                total_constraints=1,
                violations=["Dataset is empty"],
            )
        )
        return results

    # --- department check ---
    dept_col = _find_column(df, ["departamento", "departamento_nombre", "dept"])
    has_valid_departments = True
    if dept_col is not None:
        dept_values = df[dept_col].drop_nulls().to_list()
        dept_result = check_department_constraints(dept_values, dataset_name)
        results.append(dept_result)
        has_valid_departments = dept_result.satisfied

    # --- year check ---
    year_col = _find_column(df, ["ano", "anio", "año", "year"])
    has_valid_years = True
    if year_col is not None:
        year_values = df[year_col].drop_nulls().cast(int).to_list()
        year_result = check_year_constraints(year_values, dataset_name)
        results.append(year_result)
        has_valid_years = year_result.satisfied

    # --- non-negative counts ---
    count_candidates = [
        c for c in df.columns
        if any(kw in c.lower() for kw in ("cantidad", "count", "total", "n_"))
    ]
    has_non_negative = True
    for col_name in count_candidates:
        try:
            numeric_vals = df[col_name].drop_nulls().cast(float).to_list()
        except Exception:
            continue
        neg_result = check_non_negative(numeric_vals, col_name, dataset_name)
        results.append(neg_result)
        if not neg_result.satisfied:
            has_non_negative = False

    # --- sex values check ---
    sex_col = _find_column(df, ["sexo", "sexo_victima", "sexo_agresor", "genero", "sex"])
    has_valid_sex: bool | None = None
    if sex_col is not None:
        sex_values = df[sex_col].drop_nulls().cast(str).to_list()
        if sex_values:
            sex_result = check_sex_values(sex_values, dataset_name)
            results.append(sex_result)
            has_valid_sex = sex_result.satisfied

    # --- composite Z3 formula ---
    z3_sat, z3_unsat = build_z3_schema_formula(
        dataset=dataset_name,
        row_count=len(df),
        has_valid_departments=has_valid_departments,
        has_valid_years=has_valid_years,
        has_non_negative_counts=has_non_negative,
        has_valid_sex=has_valid_sex,
    )
    results.append(
        ConstraintResult(
            dataset=dataset_name,
            satisfied=z3_sat,
            total_constraints=len(z3_unsat) + (1 if z3_sat else 0),
            violations=[f"Z3 UNSAT on: {c}" for c in z3_unsat],
        )
    )

    return results


def main() -> None:
    parquet_files = sorted(PROCESSED_DIR.glob("*.parquet"))
    if not parquet_files:
        print(f"No parquet files found in {PROCESSED_DIR}")
        return

    print("=" * 70)
    print("SCHEMA VALIDATION REPORT")
    print("=" * 70)

    all_passed = True
    for pq_path in parquet_files:
        print(f"\n--- {pq_path.stem} ---")
        results = _validate_dataset(pq_path)
        for r in results:
            status_tag = "SAT" if r.satisfied else "UNSAT"
            print(f"  [{status_tag}] {r.summary()}")
            if not r.satisfied:
                all_passed = False
                for v in r.violations[:5]:
                    safe_v = str(v).encode("ascii", errors="replace").decode("ascii")
                    print(f"        ! {safe_v}")

    print("\n" + "=" * 70)
    print(f"OVERALL: {'ALL PASSED' if all_passed else 'VIOLATIONS DETECTED'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
