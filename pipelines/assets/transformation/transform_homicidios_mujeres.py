""" @bruin
name: transformation.transform_homicidios_mujeres
type: python
tags:
  - transformation
depends:
  - ingestion.ingest_tabular
description: Transform homicidios_mujeres dataset to normalized Parquet
@bruin """

from pathlib import Path

import polars as pl


RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "tabular" / "homicidios_mujeres"
OUT_PATH = Path(__file__).resolve().parents[3] / "data" / "processed" / "tabular" / "homicidios_mujeres.parquet"


def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Strip whitespace, lowercase, replace spaces with underscores."""
    rename_map = {
        col: col.strip().lower().replace(" ", "_")
        for col in df.columns
    }
    return df.rename(rename_map)


def read_csv_safe(path: Path) -> pl.DataFrame:
    """Read CSV with comma separator, fallback to semicolon with latin-1."""
    try:
        return pl.read_csv(
            path,
            separator=",",
            infer_schema_length=10000,
            ignore_errors=True,
        )
    except Exception:
        return pl.read_csv(
            path,
            separator=";",
            encoding="utf8-lossy",
            infer_schema_length=10000,
            ignore_errors=True,
        )


def read_file(path: Path) -> pl.DataFrame:
    """Read CSV or XLSX file."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv_safe(path)
    elif suffix in (".xlsx", ".xls"):
        return pl.read_excel(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def parse_date_columns(df: pl.DataFrame) -> pl.DataFrame:
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
    raw_files = sorted(
        f for f in RAW_DIR.iterdir()
        if f.suffix.lower() in (".csv", ".xlsx", ".xls")
    )
    if not raw_files:
        print("No data files found in", RAW_DIR)
        return

    frames: list[pl.DataFrame] = []
    for file_path in raw_files:
        try:
            df = read_file(file_path)
        except Exception as exc:
            print(f"Warning: skipping {file_path.name}: {exc}")
            continue

        df = normalize_columns(df)
        df = df.cast({col: pl.Utf8 for col in df.columns})
        frames.append(df)

    if not frames:
        print("No dataframes to union.")
        return

    all_cols: set[str] = set()
    for df in frames:
        all_cols.update(df.columns)

    aligned: list[pl.DataFrame] = []
    for df in frames:
        exprs = []
        for col in sorted(all_cols):
            if col in df.columns:
                exprs.append(pl.col(col))
            else:
                exprs.append(pl.lit(None).cast(pl.Utf8).alias(col))
        aligned.append(df.select(exprs))

    combined = pl.concat(aligned, how="vertical")
    combined = parse_date_columns(combined)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.write_parquet(OUT_PATH)
    print(f"Wrote {combined.height} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
