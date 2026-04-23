"""CKAN API client for Uruguay's open data catalog."""

from __future__ import annotations

import io
from pathlib import Path

import httpx

CKAN_API = "https://catalogodatos.gub.uy/api/3/action"
DEFAULT_ORG = "tic-ministerio-del-interior"
TIMEOUT = 120.0


def fetch_packages(
    client: httpx.Client,
    org: str = DEFAULT_ORG,
    rows: int = 50,
) -> list[dict]:
    """Query CKAN API for all datasets from the given organization."""
    resp = client.get(
        f"{CKAN_API}/package_search",
        params={"fq": f"organization:{org}", "rows": rows},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["result"]["results"]


def extract_resources(
    packages: list[dict],
    formats: set[str] | None = None,
) -> list[dict]:
    """Extract download URLs for resources matching the given formats."""
    if formats is None:
        formats = {"CSV", "XLSX", "SHP", "KML"}

    resources = []
    for pkg in packages:
        for res in pkg.get("resources", []):
            fmt = (res.get("format") or "").upper()
            if fmt in formats and res.get("url"):
                resources.append(
                    {
                        "package_name": pkg["name"],
                        "package_title": pkg.get("title", ""),
                        "resource_id": res["id"],
                        "resource_name": res.get("name", "unknown"),
                        "url": res["url"],
                        "format": fmt,
                    }
                )
    return resources


def download_resource(
    client: httpx.Client,
    url: str,
    dest: Path,
) -> Path | None:
    """Download a resource file to a local destination."""
    try:
        resp = client.get(url, follow_redirects=True, timeout=TIMEOUT)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"  SKIP {url}: {exc}")
        return None

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)
    print(f"  OK {dest.name} ({len(resp.content)} bytes)")
    return dest


def download_resource_bytes(
    client: httpx.Client,
    url: str,
) -> bytes | None:
    """Download a resource and return raw bytes."""
    try:
        resp = client.get(url, follow_redirects=True, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.content
    except httpx.HTTPError as exc:
        print(f"  SKIP {url}: {exc}")
        return None
