""" @bruin
name: transformation.transform_delitos
type: python
tags:
  - transformation
depends:
  - ingestion.ingest_tabular
description: Transform delitos_denunciados dataset to normalized Parquet
@bruin """

import sys
import unicodedata
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from interior_minister.schemas import normalize_department

RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "tabular" / "delitos_denunciados"
OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "tabular"


def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Strip whitespace, lowercase, replace spaces with underscores, strip accents."""
    def _normalize(name: str) -> str:
        name = name.strip().lower().replace(" ", "_")
        nfkd = unicodedata.normalize("NFKD", name)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    rename_map = {col: _normalize(col) for col in df.columns}
    return df.rename(rename_map)


def try_parse_dates(df: pl.DataFrame) -> pl.DataFrame:
    """Try to parse date columns with known formats, skip on failure."""
    date_cols = [
        col for col in df.columns
        if any(kw in col for kw in ("fecha", "date"))
    ]
    for col in date_cols:
        for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                df = df.with_columns(
                    pl.col(col).cast(pl.Utf8).str.to_date(fmt, strict=False).alias(col)
                )
                break
            except Exception:
                continue
    return df


def normalize_departments(df: pl.DataFrame) -> pl.DataFrame:
    """Normalize department columns to canonical uppercase form."""
    for col in df.columns:
        if "depart" in col or col in ("depto", "dpto"):
            df = df.with_columns(
                pl.col(col).map_elements(
                    lambda v: normalize_department(v) if v else v,
                    return_dtype=pl.Utf8,
                ).alias(col)
            )
    return df


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # These are two distinct datasets with different schemas and separators:
    # 1. Denuncias_de_otros_delitos.csv (semicolon-separated, crime reports)
    # 2. Homicidios_dolosos_consumados.csv (comma-separated, homicide victims)
    # Process each independently.

    denuncias_path = RAW_DIR / "Denuncias_de_otros_delitos.csv"
    homicidios_path = RAW_DIR / "Homicidios_dolosos_consumados.csv"

    if denuncias_path.exists():
        print(f"Processing {denuncias_path.name}...")
        raw = denuncias_path.read_bytes()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("latin-1")
        df = pl.read_csv(
            content.encode("utf-8"),
            separator=";",
            infer_schema_length=10000,
            ignore_errors=True,
        )
        df = normalize_columns(df)
        df = try_parse_dates(df)
        df = normalize_departments(df)
        out = OUT_DIR / "delitos_denuncias.parquet"
        df.write_parquet(out)
        print(f"  Wrote {df.height:,} rows to {out.name}")

    if homicidios_path.exists():
        print(f"Processing {homicidios_path.name}...")
        raw = homicidios_path.read_bytes()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("latin-1")
        df = pl.read_csv(
            content.encode("utf-8"),
            separator=",",
            infer_schema_length=10000,
            ignore_errors=True,
        )
        df = normalize_columns(df)
        df = try_parse_dates(df)
        df = normalize_departments(df)
        out = OUT_DIR / "delitos_homicidios.parquet"
        df.write_parquet(out)
        print(f"  Wrote {df.height:,} rows to {out.name}")

    # Also write a combined reference as delitos_denunciados.parquet
    # with just the shared columns (año, departamento, fecha)
    if denuncias_path.exists() and homicidios_path.exists():
        df_den = pl.read_parquet(OUT_DIR / "delitos_denuncias.parquet")
        df_hom = pl.read_parquet(OUT_DIR / "delitos_homicidios.parquet")

        # Find año column (may be año or a_o due to encoding)
        den_year_col = next((c for c in df_den.columns if "o" in c and ("a" in c or "año" in c.lower())), None)
        hom_year_col = next((c for c in df_hom.columns if "o" in c and ("a" in c or "año" in c.lower())), None)

        if den_year_col and hom_year_col:
            summary_den = (
                df_den.group_by(den_year_col)
                .len()
                .rename({den_year_col: "ano", "len": "count"})
                .with_columns(pl.lit("denuncias").alias("source"))
            )
            summary_hom = (
                df_hom.group_by(hom_year_col)
                .len()
                .rename({hom_year_col: "ano", "len": "count"})
                .with_columns(pl.lit("homicidios").alias("source"))
            )
            summary = pl.concat([summary_den, summary_hom])
            summary.write_parquet(OUT_DIR / "delitos_denunciados.parquet")
            print(f"  Summary: {summary.height} rows")


if __name__ == "__main__":
    main()
