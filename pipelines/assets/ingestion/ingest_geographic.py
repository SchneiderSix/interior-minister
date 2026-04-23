""" @bruin
name: ingestion.ingest_geographic
type: python
tags:
  - ingestion
description: Download geographic datasets from Uruguay Interior Ministry CKAN catalog
depends:
  - ingestion.ingest_tabular
@bruin """

from __future__ import annotations

import sys
import zipfile
from io import BytesIO
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from interior_minister.catalog import CKAN_API, TIMEOUT  # noqa: E402

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "geographic"

GEOGRAPHIC_DATASETS: dict[str, dict] = {
    "seccionales": {
        "slug": "tic-ministerio-del-interior-seccionales-policiales",
        "prefer": "SHP",
    },
    "comisarias": {
        "slug": "comisarias",
        "prefer": "SHP",
    },
    "jefaturas": {
        "slug": "tic-ministerio-del-interior-jefaturas",
        "prefer": "KML",  # RAR archive for SHP; use KML fallback
    },
    "bomberos": {
        "slug": "tic-ministerio-del-interior-destacamentos-d-n-b",
        "prefer": "SHP",
    },
    "cevdg": {
        "slug": "tic-ministerio-del-interior-uevdg",
        "prefer": "SHP",
    },
}

SHP_ARCHIVE_FORMATS = {"SHP", "ZIP"}
GEO_FORMATS = {"SHP", "ZIP", "KML"}


def _fetch_package_resources(client: httpx.Client, slug: str) -> list[dict]:
    """Fetch resource list for a single CKAN package."""
    resp = client.get(
        f"{CKAN_API}/package_show",
        params={"id": slug},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["result"].get("resources", [])


def _find_geo_resources(
    resources: list[dict],
    preferred_format: str,
) -> list[dict]:
    """Select geographic resources, preferring the specified format with fallback."""
    preferred: list[dict] = []
    fallback: list[dict] = []

    for res in resources:
        fmt = (res.get("format") or "").upper().strip()
        url = res.get("url", "")
        if not url:
            continue

        if fmt == preferred_format or (
            preferred_format == "SHP" and fmt in SHP_ARCHIVE_FORMATS
        ):
            preferred.append(res)
        elif fmt == "KML":
            fallback.append(res)

    if preferred:
        return preferred
    return fallback


def _download_bytes(client: httpx.Client, url: str) -> bytes | None:
    """Download raw bytes from a URL."""
    try:
        resp = client.get(url, follow_redirects=True, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.content
    except httpx.HTTPError as exc:
        print(f"  SKIP {url}: {exc}")
        return None


def _is_zip(data: bytes) -> bool:
    """Check if bytes represent a ZIP archive."""
    return data[:4] == b"PK\x03\x04"


def _extract_shp_archive(data: bytes, dest_dir: Path) -> bool:
    """Extract a ZIP archive containing shapefile components."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(BytesIO(data)) as zf:
            shp_extensions = {".shp", ".shx", ".dbf", ".prj", ".cpg", ".sbn", ".sbx"}
            extracted = 0
            for member in zf.namelist():
                # Skip directories and macOS metadata
                if member.endswith("/") or "__MACOSX" in member:
                    continue
                ext = Path(member).suffix.lower()
                if ext in shp_extensions or not shp_extensions:
                    filename = Path(member).name
                    dest_file = dest_dir / filename
                    dest_file.write_bytes(zf.read(member))
                    extracted += 1
            print(f"  Extracted {extracted} file(s) to {dest_dir.name}/")
            return extracted > 0
    except zipfile.BadZipFile:
        print(f"  ERROR: not a valid ZIP archive")
        return False


def _save_kml(data: bytes, dest_dir: Path, name: str) -> bool:
    """Save KML data to disk."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = (
        name.replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .strip("_")
    )
    if not safe_name.lower().endswith(".kml"):
        safe_name = f"{safe_name}.kml"
    dest = dest_dir / safe_name
    dest.write_bytes(data)
    print(f"  OK {dest.name} ({len(data):,} bytes)")
    return True


def main() -> None:
    """Download all geographic datasets from CKAN."""
    print("=== Ingesting geographic datasets ===")

    with httpx.Client(follow_redirects=True, timeout=TIMEOUT) as client:
        for dataset_name, cfg in GEOGRAPHIC_DATASETS.items():
            slug = cfg["slug"]
            preferred = cfg["prefer"]
            print(f"\n--- {dataset_name} (slug={slug}, prefer={preferred}) ---")
            dest_dir = RAW_DIR / dataset_name

            try:
                resources = _fetch_package_resources(client, slug)
            except httpx.HTTPError as exc:
                print(f"  ERROR fetching package metadata: {exc}")
                continue

            geo_resources = _find_geo_resources(resources, preferred)
            if not geo_resources:
                print("  WARNING: no geographic resources found, skipping")
                continue

            print(f"  Found {len(geo_resources)} geographic resource(s)")

            for res in geo_resources:
                url = res.get("url", "")
                fmt = (res.get("format") or "").upper().strip()
                name = res.get("name") or res.get("id", "unknown")

                data = _download_bytes(client, url)
                if data is None:
                    continue

                if fmt in SHP_ARCHIVE_FORMATS or _is_zip(data):
                    _extract_shp_archive(data, dest_dir)
                elif fmt == "KML" or url.lower().endswith(".kml"):
                    _save_kml(data, dest_dir, name)
                else:
                    # Save raw file as-is
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    safe_name = name.replace("/", "_").replace("\\", "_").replace(" ", "_")
                    dest = dest_dir / safe_name
                    dest.write_bytes(data)
                    print(f"  OK {dest.name} ({len(data):,} bytes)")

    print("\n=== Geographic ingestion complete ===")


if __name__ == "__main__":
    main()
