"""Format converters: CSV/XLSX/SHP -> Parquet."""

from __future__ import annotations

from pathlib import Path

import polars as pl


def csv_to_parquet(
    src: Path,
    dst: Path,
    separator: str = ",",
    encoding: str = "utf-8",
    infer_schema_length: int = 10000,
) -> pl.DataFrame:
    """Read a CSV file and write it as Parquet. Returns the DataFrame."""
    try:
        df = pl.read_csv(
            src,
            separator=separator,
            encoding=encoding,
            infer_schema_length=infer_schema_length,
            ignore_errors=True,
        )
    except Exception:
        df = pl.read_csv(
            src,
            separator=";",
            encoding="latin-1",
            infer_schema_length=infer_schema_length,
            ignore_errors=True,
        )

    dst.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(dst)
    return df


def xlsx_to_parquet(
    src: Path,
    dst: Path,
    sheet_name: str | int = 0,
) -> pl.DataFrame:
    """Read an XLSX file and write it as Parquet. Returns the DataFrame."""
    df = pl.read_excel(src, sheet_name=sheet_name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(dst)
    return df


def shp_to_geoparquet(
    src: Path,
    dst: Path,
    target_crs: str = "EPSG:4326",
) -> None:
    """Read a Shapefile and write it as GeoParquet, reprojecting to target CRS."""
    import geopandas as gpd

    gdf = gpd.read_file(src)
    if gdf.crs is not None and str(gdf.crs) != target_crs:
        gdf = gdf.to_crs(target_crs)
    elif gdf.crs is None:
        gdf = gdf.set_crs(target_crs)

    dst.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(dst)


def kml_to_geoparquet(
    src: Path,
    dst: Path,
    target_crs: str = "EPSG:4326",
) -> None:
    """Read a KML file and write it as GeoParquet."""
    import geopandas as gpd

    gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "r"
    gdf = gpd.read_file(src, driver="KML")
    if gdf.crs is not None and str(gdf.crs) != target_crs:
        gdf = gdf.to_crs(target_crs)

    dst.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(dst)
