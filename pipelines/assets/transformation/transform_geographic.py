""" @bruin
name: transformation.transform_geographic
type: python
tags:
  - transformation
depends:
  - ingestion.ingest_geographic
description: Transform geographic datasets (SHP/KML) to normalized GeoParquet
@bruin """

from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree as ET

import sys

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon, MultiPolygon

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from interior_minister.schemas import normalize_department


RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "geographic"
OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "geographic"

TARGET_CRS = "EPSG:4326"

DATASETS = [
    "seccionales",
    "comisarias",
    "bomberos",
    "cevdg",
    "jefaturas",
]

KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}

# Regex to extract key-value pairs from HTML table cells in KML descriptions
# Matches patterns like: <td>KEY</td>\n\n<td>VALUE</td>
_HTML_TABLE_RE = re.compile(
    r"<td>\s*([A-Z_0-9]+)\s*</td>\s*<td>\s*(.*?)\s*</td>",
    re.IGNORECASE,
)


def normalize_columns(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Strip whitespace, lowercase, replace spaces with underscores."""
    gdf.columns = [
        col.strip().lower().replace(" ", "_")
        for col in gdf.columns
    ]
    return gdf


def find_geo_file(directory: Path, extension: str) -> Path | None:
    """Find the first file with the given extension in a directory tree."""
    matches = sorted(directory.glob(f"**/*{extension}"))
    return matches[0] if matches else None


def _parse_kml_coordinates(coord_text: str) -> list[tuple[float, float]]:
    """Parse KML coordinate string into list of (lon, lat) tuples."""
    coords = []
    for token in coord_text.strip().split():
        parts = token.split(",")
        if len(parts) >= 2:
            coords.append((float(parts[0]), float(parts[1])))
    return coords


def _parse_html_description(html: str) -> dict[str, str]:
    """Extract key-value pairs from HTML table embedded in KML descriptions."""
    pairs = _HTML_TABLE_RE.findall(html)
    result: dict[str, str] = {}
    for key, val in pairs:
        key = key.strip()
        val = val.strip()
        if key and val:
            result[key] = val
    return result


def read_kml(kml_path: Path) -> gpd.GeoDataFrame:
    """Parse a KML file into a GeoDataFrame using xml.etree (no Fiona needed)."""
    tree = ET.parse(kml_path)
    root = tree.getroot()

    records: list[dict] = []
    # Find all Placemark elements
    for pm in root.iter(f"{{{KML_NS['kml']}}}Placemark"):
        row: dict = {}

        # Description — parse first, may contain structured HTML table
        desc_el = pm.find("kml:description", KML_NS)
        if desc_el is not None and desc_el.text:
            desc_text = desc_el.text.strip()
            if "<td>" in desc_text:
                html_attrs = _parse_html_description(desc_text)
                row.update({k.lower(): v for k, v in html_attrs.items()})
            else:
                row["descripcion"] = desc_text

        # Name — only use Placemark name if no structured attrs provided it
        if "nombre" not in row:
            name_el = pm.find("kml:name", KML_NS)
            if name_el is not None and name_el.text:
                row["nombre"] = name_el.text.strip()

        # ExtendedData / SimpleData fields
        for sd in pm.iter(f"{{{KML_NS['kml']}}}SimpleData"):
            field_name = sd.get("name", "").strip().lower()
            if field_name and sd.text:
                row[field_name] = sd.text.strip()

        # Also check Data elements
        for data_el in pm.iter(f"{{{KML_NS['kml']}}}Data"):
            field_name = data_el.get("name", "").strip().lower()
            val_el = data_el.find("kml:value", KML_NS)
            if field_name and val_el is not None and val_el.text:
                row[field_name] = val_el.text.strip()

        # Geometry: Point
        point_el = pm.find(".//kml:Point/kml:coordinates", KML_NS)
        if point_el is not None and point_el.text:
            coords = _parse_kml_coordinates(point_el.text)
            if coords:
                row["geometry"] = Point(coords[0])
                records.append(row)
                continue

        # Geometry: Polygon
        poly_el = pm.find(".//kml:Polygon//kml:coordinates", KML_NS)
        if poly_el is not None and poly_el.text:
            coords = _parse_kml_coordinates(poly_el.text)
            if len(coords) >= 3:
                row["geometry"] = Polygon(coords)
                records.append(row)
                continue

        # Geometry: MultiGeometry with Polygons
        multi_el = pm.find(".//kml:MultiGeometry", KML_NS)
        if multi_el is not None:
            polys = []
            for pg in multi_el.iter(f"{{{KML_NS['kml']}}}Polygon"):
                c_el = pg.find(".//kml:coordinates", KML_NS)
                if c_el is not None and c_el.text:
                    coords = _parse_kml_coordinates(c_el.text)
                    if len(coords) >= 3:
                        polys.append(Polygon(coords))
            if polys:
                row["geometry"] = MultiPolygon(polys) if len(polys) > 1 else polys[0]
                records.append(row)
                continue

    if not records:
        raise ValueError(f"No placemarks with geometry found in {kml_path.name}")

    gdf = gpd.GeoDataFrame(records, crs=TARGET_CRS)
    return gdf


def process_dataset(name: str) -> None:
    """Read, reproject, normalize, and write a single geographic dataset."""
    dataset_dir = RAW_DIR / name
    if not dataset_dir.exists():
        print(f"Warning: directory not found: {dataset_dir}")
        return

    # Prefer SHP if available, fall back to KML
    shp_file = find_geo_file(dataset_dir, ".shp")
    kml_file = find_geo_file(dataset_dir, ".kml")

    if shp_file:
        print(f"Reading {name} from {shp_file.name} (SHP)")
        gdf = gpd.read_file(shp_file)
    elif kml_file:
        print(f"Reading {name} from {kml_file.name} (KML)")
        gdf = read_kml(kml_file)
    else:
        print(f"Warning: no SHP/KML file found for {name}")
        return

    if gdf.crs is None:
        print(f"  Warning: {name} has no CRS, assuming EPSG:4326")
        gdf = gdf.set_crs(TARGET_CRS)
    elif str(gdf.crs) != TARGET_CRS:
        print(f"  Reprojecting {name} from {gdf.crs} to {TARGET_CRS}")
        gdf = gdf.to_crs(TARGET_CRS)

    gdf = normalize_columns(gdf)

    # Normalize department values
    for dept_col in ["departamen", "depto", "dpto"]:
        if dept_col in gdf.columns:
            gdf[dept_col] = gdf[dept_col].apply(
                lambda v: normalize_department(v) if pd.notna(v) else v
            )

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
