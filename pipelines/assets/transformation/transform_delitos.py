""" @bruin
name: transformation.transform_delitos
type: python
tags:
  - transformation
depends:
  - ingestion.ingest_tabular
description: Transform delitos_denunciados dataset to normalized Parquet
@bruin """

from pathlib import Path

import polars as pl


RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "tabular" / "delitos_denunciados"
OUT_PATH = Path(__file__).resolve().parents[3] / "data" / "processed" / "tabular" / "delitos_denunciados.parquet"


def normalize_columns(df: pl.LazyFrame) -> pl.LazyFrame:
    """Strip whitespace, lowercase, replace spaces with underscores."""
    rename_map = {
        col: col.strip().lower().replace(" ", "_")
        for col in df.columns
    }
    return df.rename(rename_map)


def read_csv_safe(path: Path) -> pl.LazyFrame:
    """Read CSV with comma separator, fallback to semicolon with latin-1."""
    try:
        return pl.scan_csv(
            path,
            separator=",",
            infer_schema_length=10000,
            ignore_errors=True,
        )
    except Exception:
        return pl.scan_csv(
            path,
            separator=";",
            encoding="utf8-lossy",
            infer_schema_length=10000,
            ignore_errors=True,
        )


def parse_date_columns(df: pl.LazyFrame) -> pl.LazyFrame:
    """Attempt to parse columns whose name contains 'fecha' or 'date' as Date."""
    date_cols = [
        col for col in df.columns
        if any(kw in col for kw in ("fecha", "date", "periodo"))
    ]
    for col in date_cols:
        df = df.with_columns(
            pl.col(col).cast(pl.Utf8).str.to_date(strict=False).alias(col)
        )
    return df


def main() -> None:
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in", RAW_DIR)
        return

    frames: list[pl.LazyFrame] = []
    for csv_path in csv_files:
        lf = read_csv_safe(csv_path)
        lf = normalize_columns(lf)
        frames.append(lf)

    if not frames:
        print("No dataframes to union.")
        return

    # Align schemas by casting all columns to Utf8 before union, then re-infer
    all_cols: set[str] = set()
    for lf in frames:
        all_cols.update(lf.columns)

    aligned: list[pl.LazyFrame] = []
    for lf in frames:
        exprs = []
        for col in sorted(all_cols):
            if col in lf.columns:
                exprs.append(pl.col(col).cast(pl.Utf8))
            else:
                exprs.append(pl.lit(None).alias(col))
        aligned.append(lf.select(exprs))

    combined = pl.concat(aligned, how="vertical")
    combined = parse_date_columns(combined)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.collect().write_parquet(OUT_PATH)
    row_count = pl.scan_parquet(OUT_PATH).select(pl.len()).collect().item()
    print(f"Wrote {row_count} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
