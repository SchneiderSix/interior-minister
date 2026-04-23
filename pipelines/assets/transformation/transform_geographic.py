""" @bruin
name: transformation.transform_geographic
type: python
tags:
  - transformation
depends:
  - ingestion.ingest_geographic
description: Transform geographic datasets (SHP/KML) to normalized GeoParquet
@bruin """

from pathlib import Path

import geopandas as gpd


RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "geographic"
OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "geographic"

TARGET_CRS = "EPSG:4326"

DATASETS = [
    "seccionales",
    "comisarias",
    "jefaturas",
    "bomberos",
    "cevdg",
]


def normalize_columns(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Strip whitespace, lowercase, replace spaces with underscores."""
    gdf.columns = [
        col.strip().lower().replace(" ", "_")
        for col in gdf.columns
    ]
    return gdf


def find_geo_file(directory: Path) -> Path | None:
    """Find the first SHP or KML file in a directory tree."""
    for pattern in ("**/*.shp", "**/*.kml"):
        matches = sorted(directory.glob(pattern))
        if matches:
            return matches[0]
    return None


def process_dataset(name: str) -> None:
    """Read, reproject, normalize, and write a single geographic dataset."""
    dataset_dir = RAW_DIR / name
    if not dataset_dir.exists():
        print(f"Warning: directory not found: {dataset_dir}")
        return

    geo_file = find_geo_file(dataset_dir)
    if geo_file is None:
        # Try reading directly from RAW_DIR if files are not in subdirectories
        geo_file = find_geo_file(RAW_DIR)
        if geo_file is None or name not in geo_file.stem.lower():
            print(f"Warning: no SHP/KML file found for {name}")
            return

    print(f"Reading {name} from {geo_file}")

    suffix = geo_file.suffix.lower()
    if suffix == ".kml":
        gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
        gdf = gpd.read_file(geo_file, driver="KML")
    else:
        gdf = gpd.read_file(geo_file)

    if gdf.crs is None:
        print(f"  Warning: {name} has no CRS, assuming EPSG:4326")
        gdf = gdf.set_crs(TARGET_CRS)
    elif str(gdf.crs) != TARGET_CRS:
        print(f"  Reprojecting {name} from {gdf.crs} to {TARGET_CRS}")
        gdf = gdf.to_crs(TARGET_CRS)

    gdf = normalize_columns(gdf)

    out_path = OUT_DIR / f"{name}.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(out_path)
    print(f"  Wrote {len(gdf)} features to {out_path}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for dataset_name in DATASETS:
        try:
            process_dataset(dataset_name)
        except Exception as exc:
            print(f"Error processing {dataset_name}: {exc}")

    print("Geographic transformation complete.")


if __name__ == "__main__":
    main()
