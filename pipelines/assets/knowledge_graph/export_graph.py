""" @bruin
name: knowledge_graph.export_graph
type: python
tags:
  - knowledge_graph
depends:
  - knowledge_graph.build_graph
description: Export knowledge graph to TTL and JSON-LD, upload to GCS
@bruin """

from __future__ import annotations

import sys
from pathlib import Path

from rdflib import Graph

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from interior_minister.gcs import upload_file

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KG_DIR = PROJECT_ROOT / "data" / "knowledge_graph"
TTL_INPUT = KG_DIR / "crime_graph.ttl"
JSONLD_OUTPUT = KG_DIR / "crime_graph.jsonld"

GCS_PREFIX = "knowledge_graph"


def _load_graph(path: Path) -> Graph:
    """Load an RDF graph from a Turtle file."""
    g = Graph()
    g.parse(str(path), format="turtle")
    return g


def _serialize_formats(g: Graph) -> list[Path]:
    """Serialize the graph to TTL and JSON-LD, return output paths."""
    outputs: list[Path] = []

    # TTL is already on disk from build_graph; re-serialize to ensure consistency
    ttl_path = KG_DIR / "crime_graph.ttl"
    g.serialize(str(ttl_path), format="turtle")
    outputs.append(ttl_path)
    print(f"  Serialized TTL: {ttl_path} ({ttl_path.stat().st_size:,} bytes)")

    # JSON-LD
    g.serialize(str(JSONLD_OUTPUT), format="json-ld")
    outputs.append(JSONLD_OUTPUT)
    print(f"  Serialized JSON-LD: {JSONLD_OUTPUT} ({JSONLD_OUTPUT.stat().st_size:,} bytes)")

    return outputs


def _upload_to_gcs(paths: list[Path]) -> list[str]:
    """Upload each serialized file to GCS."""
    uris: list[str] = []
    for path in paths:
        try:
            uri = upload_file(path, GCS_PREFIX)
            uris.append(uri)
        except Exception as exc:
            print(f"  WARNING: failed to upload {path.name}: {exc}")
    return uris


def main() -> None:
    if not TTL_INPUT.exists():
        print(f"ERROR: TTL graph not found at {TTL_INPUT}")
        print("Run knowledge_graph.build_graph first.")
        return

    print("Exporting knowledge graph ...")

    g = _load_graph(TTL_INPUT)
    print(f"  Loaded graph: {len(g)} triples")

    output_paths = _serialize_formats(g)

    print("\nUploading to GCS ...")
    uris = _upload_to_gcs(output_paths)

    if uris:
        print(f"\n  Uploaded {len(uris)} files to GCS:")
        for uri in uris:
            print(f"    {uri}")
    else:
        print("\n  WARNING: no files were uploaded (check GCS credentials)")

    print("\nDone.")


if __name__ == "__main__":
    main()
