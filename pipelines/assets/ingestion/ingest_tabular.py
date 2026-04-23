""" @bruin
name: ingestion.ingest_tabular
type: python
tags:
  - ingestion
description: Download tabular datasets from Uruguay Interior Ministry CKAN catalog
depends: []
@bruin """

from __future__ import annotations

import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from interior_minister.catalog import CKAN_API, TIMEOUT  # noqa: E402

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "tabular"

TABULAR_DATASETS: dict[str, str] = {
    "delitos_denunciados": "ministerio-del-interior-delitos_denunciados_en_el_uruguay",
    "violencia_domestica": "violencia-domestica-y-asociados",
    "delitos_sexuales": "delitos-sexuales",
    "homicidios_mujeres": "homicidios-a-mujeres",
    "medidas_alternativas": "ministerio-del-interior-medidas-alternativas",
    "sistema_carcelario": "ministerio-del-interior-sistema-carcelario",
}

PREFERRED_FORMATS = ("CSV", "XLSX")
SKIP_FORMATS = {"JSON", "XML", "RDF", "HTML"}


def _pick_tabular_resources(resources: list[dict]) -> list[dict]:
    """Filter resources to CSV/XLSX, preferring CSV when both exist."""
    picked: list[dict] = []
    for res in resources:
        fmt = (res.get("format") or "").upper().strip()
        if fmt in SKIP_FORMATS:
            continue
        if fmt in PREFERRED_FORMATS:
            picked.append(res)
    return picked


def _download_file(client: httpx.Client, url: str, dest: Path) -> bool:
    """Download a single file. Returns True on success."""
    try:
        resp = client.get(url, follow_redirects=True, timeout=TIMEOUT)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"  SKIP {url}: {exc}")
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)
    print(f"  OK {dest.name} ({len(resp.content):,} bytes)")
    return True


def _fetch_package_resources(client: httpx.Client, slug: str) -> list[dict]:
    """Fetch resource list for a single CKAN package."""
    resp = client.get(
        f"{CKAN_API}/package_show",
        params={"id": slug},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["result"].get("resources", [])


def _extension_for_format(fmt: str) -> str:
    """Map CKAN format string to file extension."""
    mapping = {"CSV": ".csv", "XLSX": ".xlsx"}
    return mapping.get(fmt.upper(), f".{fmt.lower()}")


def main() -> None:
    """Download all tabular datasets from CKAN."""
    print("=== Ingesting tabular datasets ===")

    with httpx.Client(follow_redirects=True, timeout=TIMEOUT) as client:
        for dataset_name, slug in TABULAR_DATASETS.items():
            print(f"\n--- {dataset_name} (slug={slug}) ---")
            dest_dir = RAW_DIR / dataset_name

            try:
                resources = _fetch_package_resources(client, slug)
            except httpx.HTTPError as exc:
                print(f"  ERROR fetching package metadata: {exc}")
                continue

            tabular = _pick_tabular_resources(resources)
            if not tabular:
                print("  WARNING: no CSV/XLSX resources found, skipping")
                continue

            print(f"  Found {len(tabular)} tabular resource(s)")

            for res in tabular:
                url = res.get("url", "")
                fmt = (res.get("format") or "").upper().strip()
                name = res.get("name") or res.get("id", "unknown")

                # Sanitize filename
                safe_name = (
                    name.replace("/", "_")
                    .replace("\\", "_")
                    .replace(" ", "_")
                    .strip("_")
                )
                ext = _extension_for_format(fmt)
                if not safe_name.lower().endswith(ext):
                    safe_name = f"{safe_name}{ext}"

                dest = dest_dir / safe_name
                _download_file(client, url, dest)

    print("\n=== Tabular ingestion complete ===")


if __name__ == "__main__":
    main()
