""" @bruin
name: transformation.transform_sistema_carcelario
type: python
tags:
  - transformation
depends:
  - ingestion.ingest_tabular
description: Transform sistema_carcelario dataset to normalized Parquet
@bruin """

import unicodedata
from pathlib import Path

import polars as pl


RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "tabular" / "sistema_carcelario"
OUT_PATH = Path(__file__).resolve().parents[3] / "data" / "processed" / "tabular" / "sistema_carcelario.parquet"


def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Strip whitespace, lowercase, replace spaces with underscores, strip accents."""
    def _normalize(name: str) -> str:
        name = name.strip().lower().replace(" ", "_")
        nfkd = unicodedata.normalize("NFKD", name)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    rename_map = {col: _normalize(col) for col in df.columns}
    return df.rename(rename_map)


def read_csv_safe(path: Path) -> pl.DataFrame:
    """Read CSV with proper encoding detection (UTF-8 → Latin-1 fallback)."""
    raw = path.read_bytes()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        content = raw.decode("latin-1")
    utf8_bytes = content.encode("utf-8")

    for sep in (",", ";"):
        try:
            df = pl.read_csv(
                utf8_bytes,
                separator=sep,
                infer_schema_length=10000,
                ignore_errors=True,
            )
            if len(df.columns) > 1:
                return df
        except Exception:
            continue
    return pl.read_csv(
        utf8_bytes,
        separator=";",
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
    """Try to parse date columns with known formats, skip on failure."""
    date_cols = [
        col for col in df.columns
        if any(kw in col for kw in ("fecha", "date", "periodo"))
    ]
    for col in date_cols:
        parsed = False
        for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                df = df.with_columns(
                    pl.col(col).cast(pl.Utf8).str.to_date(fmt, strict=False).alias(col)
                )
                parsed = True
                break
            except Exception:
                continue
        if not parsed:
            print(f"  Warning: could not parse date column '{col}', keeping as string")
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
