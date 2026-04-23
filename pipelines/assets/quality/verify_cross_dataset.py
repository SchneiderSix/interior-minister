""" @bruin
name: quality.verify_cross_dataset
type: python
tags:
  - quality
depends:
  - quality.verify_schemas
description: Cross-dataset consistency checks across crime, corrections, and DV data
@bruin """

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "tabular"


def _read_if_exists(name: str) -> pl.DataFrame | None:
    """Read a processed parquet file by dataset stem name, or return None."""
    path = PROCESSED_DIR / f"{name}.parquet"
    if path.exists():
        return pl.read_parquet(path)
    return None


def _find_column(df: pl.DataFrame, candidates: list[str]) -> str | None:
    lower_map = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def check_dv_subset_consistency() -> list[str]:
    """DV records in delitos_denunciados should be consistent with violencia_domestica."""
    issues: list[str] = []
    delitos = _read_if_exists("delitos_denunciados")
    vd = _read_if_exists("violencia_domestica")

    if delitos is None or vd is None:
        issues.append("SKIP: delitos_denunciados or violencia_domestica not found")
        return issues

    year_col_delitos = _find_column(delitos, ["anio", "año", "year"])
    year_col_vd = _find_column(vd, ["anio", "año", "year"])
    if year_col_delitos is None or year_col_vd is None:
        issues.append("SKIP: year column not found in one of the datasets")
        return issues

    # Filter delitos to DV-related rows
    titulo_col = _find_column(delitos, ["titulo", "subtitulo"])
    if titulo_col is not None:
        dv_delitos = delitos.filter(
            pl.col(titulo_col).str.to_lowercase().str.contains("violencia dom")
            | pl.col(titulo_col).str.to_lowercase().str.contains("v.d.")
            | pl.col(titulo_col).str.to_lowercase().str.contains("domestica")
        )
    else:
        issues.append("SKIP: no titulo column for DV filtering")
        return issues

    delitos_years = set(
        dv_delitos[year_col_delitos].drop_nulls().cast(int).unique().to_list()
    )
    vd_years = set(
        vd[year_col_vd].drop_nulls().cast(int).unique().to_list()
    )
    overlap = delitos_years & vd_years

    if not overlap:
        issues.append("WARNING: no year overlap between DV in delitos and VD dataset")
    else:
        for year in sorted(overlap):
            dv_count = len(
                dv_delitos.filter(pl.col(year_col_delitos).cast(int) == year)
            )
            vd_count = len(vd.filter(pl.col(year_col_vd).cast(int) == year))
            if vd_count > dv_count * 1.5:
                issues.append(
                    f"  Year {year}: VD dataset ({vd_count}) has >50% more than "
                    f"DV subset in delitos ({dv_count})"
                )

    return issues


def check_female_homicides_subset() -> list[str]:
    """Female homicides should be a subset of total homicides by count."""
    issues: list[str] = []
    delitos = _read_if_exists("delitos_denunciados")
    hom_mujeres = _read_if_exists("homicidios_mujeres")

    if delitos is None or hom_mujeres is None:
        issues.append("SKIP: delitos_denunciados or homicidios_mujeres not found")
        return issues

    year_col_d = _find_column(delitos, ["anio", "año", "year"])
    year_col_h = _find_column(hom_mujeres, ["anio", "año", "year"])
    if year_col_d is None or year_col_h is None:
        issues.append("SKIP: year column not found")
        return issues

    titulo_col = _find_column(delitos, ["titulo", "subtitulo"])
    if titulo_col is not None:
        hom_delitos = delitos.filter(
            pl.col(titulo_col).str.to_lowercase().str.contains("homicidio")
        )
    else:
        issues.append("SKIP: no titulo column for homicide filtering")
        return issues

    overlap_years = set(
        hom_delitos[year_col_d].drop_nulls().cast(int).unique().to_list()
    ) & set(
        hom_mujeres[year_col_h].drop_nulls().cast(int).unique().to_list()
    )

    for year in sorted(overlap_years):
        total_hom = len(
            hom_delitos.filter(pl.col(year_col_d).cast(int) == year)
        )
        fem_hom = len(
            hom_mujeres.filter(pl.col(year_col_h).cast(int) == year)
        )
        if fem_hom > total_hom:
            issues.append(
                f"  Year {year}: female homicides ({fem_hom}) exceed "
                f"total homicides ({total_hom})"
            )

    return issues


def check_corrections_total() -> list[str]:
    """Prison population + alternative measures should approximate total corrections."""
    issues: list[str] = []
    prison = _read_if_exists("sistema_carcelario")
    alt = _read_if_exists("medidas_alternativas")

    if prison is None or alt is None:
        issues.append("SKIP: sistema_carcelario or medidas_alternativas not found")
        return issues

    year_col_p = _find_column(prison, ["anio", "año", "year"])
    year_col_a = _find_column(alt, ["anio", "año", "year"])
    if year_col_p is None or year_col_a is None:
        issues.append("SKIP: year column not found")
        return issues

    overlap_years = set(
        prison[year_col_p].drop_nulls().cast(int).unique().to_list()
    ) & set(
        alt[year_col_a].drop_nulls().cast(int).unique().to_list()
    )

    for year in sorted(overlap_years):
        p_count = len(prison.filter(pl.col(year_col_p).cast(int) == year))
        a_count = len(alt.filter(pl.col(year_col_a).cast(int) == year))
        total = p_count + a_count
        issues.append(
            f"  Year {year}: prison={p_count} + alt_measures={a_count} = total_corrections={total}"
        )

    return issues


def check_temporal_gaps() -> list[str]:
    """Detect missing year-month combinations in datasets that have both columns."""
    issues: list[str] = []

    for pq_path in sorted(PROCESSED_DIR.glob("*.parquet")):
        df = pl.read_parquet(pq_path)
        year_col = _find_column(df, ["anio", "año", "year"])
        month_col = _find_column(df, ["mes", "month"])

        if year_col is None or month_col is None:
            continue

        try:
            ym = (
                df.select(
                    pl.col(year_col).cast(int).alias("year"),
                    pl.col(month_col).cast(int).alias("month"),
                )
                .drop_nulls()
                .unique()
                .sort(["year", "month"])
            )
        except Exception:
            continue

        if len(ym) == 0:
            continue

        years = ym["year"].to_list()
        months = ym["month"].to_list()
        present = {(y, m) for y, m in zip(years, months)}
        min_year, max_year = min(years), max(years)

        expected = {
            (y, m)
            for y in range(min_year, max_year + 1)
            for m in range(1, 13)
        }
        missing = sorted(expected - present)
        if missing:
            sample = missing[:5]
            suffix = f" ... and {len(missing) - 5} more" if len(missing) > 5 else ""
            formatted = ", ".join(f"{y}-{m:02d}" for y, m in sample)
            issues.append(
                f"  {pq_path.stem}: {len(missing)} missing year-month combos "
                f"(e.g. {formatted}{suffix})"
            )

    return issues


def main() -> None:
    print("=" * 70)
    print("CROSS-DATASET CONSISTENCY REPORT")
    print("=" * 70)

    checks = [
        ("DV subset consistency", check_dv_subset_consistency),
        ("Female homicides subset", check_female_homicides_subset),
        ("Corrections total", check_corrections_total),
        ("Temporal gap detection", check_temporal_gaps),
    ]

    has_issues = False
    for title, check_fn in checks:
        print(f"\n--- {title} ---")
        results = check_fn()
        if not results:
            print("  OK: no issues detected")
        else:
            for line in results:
                print(line)
                if "WARNING" in line or "exceed" in line or ">50%" in line:
                    has_issues = True

    print("\n" + "=" * 70)
    print(f"OVERALL: {'ISSUES DETECTED' if has_issues else 'CONSISTENT'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
