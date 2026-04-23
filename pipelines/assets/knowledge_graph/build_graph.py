""" @bruin
name: knowledge_graph.build_graph
type: python
tags:
  - knowledge_graph
depends:
  - transformation.upload_gcs
description: Build RDF and NetworkX knowledge graphs from processed data and ontology
@bruin """

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import networkx as nx
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from interior_minister.graph import (
    add_facility,
    add_incident,
    create_rdf_graph,
    graph_stats,
    load_ontology,
    rdf_to_networkx,
    serialize_graph,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ONTOLOGY_DIR = PROJECT_ROOT / "ontology"
PROCESSED_TABULAR = PROJECT_ROOT / "data" / "processed" / "tabular"
PROCESSED_GEO = PROJECT_ROOT / "data" / "processed" / "geographic"
KG_OUTPUT_DIR = PROJECT_ROOT / "data" / "knowledge_graph"

RDF_OUTPUT = KG_OUTPUT_DIR / "crime_graph.ttl"
STATS_OUTPUT = KG_OUTPUT_DIR / "graph_stats.json"


def _find_column(df: pl.DataFrame, candidates: list[str]) -> str | None:
    lower_map = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def _stable_id(*parts: str | int | None) -> str:
    """Generate a deterministic short ID from the parts."""
    raw = "|".join(str(p) for p in parts if p is not None)
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _ingest_crime_data(g, nx_graph: nx.DiGraph) -> int:
    """Ingest crime incident data from processed parquet files."""
    crime_datasets = [
        "delitos_denunciados",
        "violencia_domestica",
        "delitos_sexuales",
        "homicidios_mujeres",
    ]
    total = 0

    for ds_name in crime_datasets:
        path = PROCESSED_TABULAR / f"{ds_name}.parquet"
        if not path.exists():
            print(f"  SKIP: {path.name} not found")
            continue

        df = pl.read_parquet(path)
        year_col = _find_column(df, ["anio", "año", "year"])
        month_col = _find_column(df, ["mes", "month"])
        dept_col = _find_column(df, ["departamento", "departamento_nombre"])
        secc_col = _find_column(df, ["seccional"])
        type_col = _find_column(df, ["titulo", "subtitulo", "tipo_delito"])

        if year_col is None or dept_col is None:
            print(f"  SKIP: {ds_name} missing year or department column")
            continue

        for row in df.iter_rows(named=True):
            year_val = row.get(year_col) if year_col else None
            month_val = row.get(month_col) if month_col else None
            dept_val = row.get(dept_col) if dept_col else None
            secc_val = row.get(secc_col) if secc_col else None
            type_val = row.get(type_col) if type_col else ds_name

            if year_val is None or dept_val is None:
                continue

            try:
                year_int = int(year_val)
            except (ValueError, TypeError):
                continue

            month_int: int | None = None
            if month_val is not None:
                try:
                    month_int = int(month_val)
                except (ValueError, TypeError):
                    pass

            incident_id = _stable_id(ds_name, year_val, month_val, dept_val, secc_val, type_val)
            incident_uri = add_incident(
                g,
                incident_id=incident_id,
                crime_type=str(type_val) if type_val else ds_name,
                department=str(dept_val),
                seccional=str(secc_val) if secc_val else None,
                year=year_int,
                month=month_int,
            )

            # Mirror in NetworkX
            nx_graph.add_node(
                str(incident_uri),
                type="Incident",
                crime_type=str(type_val),
                department=str(dept_val),
                year=year_int,
            )
            total += 1

        print(f"  {ds_name}: {len(df)} rows ingested")

    return total


def _ingest_geographic_data(g, nx_graph: nx.DiGraph) -> int:
    """Ingest facility/geographic data."""
    total = 0

    geo_files = list(PROCESSED_GEO.glob("*.parquet")) if PROCESSED_GEO.exists() else []
    for geo_path in sorted(geo_files):
        df = pl.read_parquet(geo_path)
        name_col = _find_column(df, ["nombre", "name", "establecimiento", "denominacion"])
        lat_col = _find_column(df, ["latitud", "latitude", "lat", "y"])
        lon_col = _find_column(df, ["longitud", "longitude", "lon", "lng", "x"])
        dept_col = _find_column(df, ["departamento", "departamento_nombre"])

        # Determine facility type from filename
        stem = geo_path.stem.lower()
        if "policia" in stem or "comisaria" in stem or "seccional" in stem:
            facility_type = "police"
        elif "bombero" in stem or "fire" in stem:
            facility_type = "fire"
        elif "carcel" in stem or "prison" in stem or "penitenci" in stem:
            facility_type = "prison"
        elif "cevdg" in stem or "genero" in stem:
            facility_type = "cevdg"
        else:
            facility_type = "other"

        for row in df.iter_rows(named=True):
            name_val = row.get(name_col) if name_col else geo_path.stem
            if name_val is None:
                continue

            lat_val: float | None = None
            lon_val: float | None = None
            if lat_col and lon_col:
                try:
                    lat_val = float(row[lat_col]) if row.get(lat_col) is not None else None
                    lon_val = float(row[lon_col]) if row.get(lon_col) is not None else None
                except (ValueError, TypeError):
                    pass

            dept_val = row.get(dept_col) if dept_col else None
            facility_uri = add_facility(
                g,
                name=str(name_val),
                facility_type=facility_type,
                lat=lat_val,
                lon=lon_val,
                department=str(dept_val) if dept_val else None,
            )

            nx_graph.add_node(
                str(facility_uri),
                type="Facility",
                facility_type=facility_type,
                name=str(name_val),
            )
            if dept_val:
                dept_node = f"http://interior-minister.gub.uy/ontology/location#department/{str(dept_val).replace(' ', '_')}"
                nx_graph.add_edge(str(facility_uri), dept_node, predicate="locatedIn")

            total += 1

        print(f"  {geo_path.stem}: {len(df)} facilities ingested (type={facility_type})")

    return total


def _build_department_hierarchy(g, nx_graph: nx.DiGraph) -> None:
    """Ensure all 19 department nodes exist in the graph."""
    from interior_minister.schemas import DEPARTMENTS

    from rdflib import Literal, Namespace
    from rdflib.namespace import RDF, RDFS

    LOC = Namespace("http://interior-minister.gub.uy/ontology/location#")

    for code, name in DEPARTMENTS.items():
        dept_uri = LOC[f"department/{name.replace(' ', '_')}"]
        g.add((dept_uri, RDF.type, LOC.Department))
        g.add((dept_uri, RDFS.label, Literal(name)))

        nx_node = str(dept_uri)
        nx_graph.add_node(nx_node, type="Department", name=name, code=code)


def main() -> None:
    KG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Building knowledge graph ...")

    # Create RDF graph and load ontology
    g = create_rdf_graph()
    if ONTOLOGY_DIR.exists():
        g = load_ontology(g, ONTOLOGY_DIR)
        print(f"  Loaded ontology ({len(g)} initial triples)")
    else:
        print("  WARNING: ontology directory not found, building without base ontology")

    nx_graph = nx.DiGraph()

    # Department hierarchy
    _build_department_hierarchy(g, nx_graph)
    print(f"  Department hierarchy: 19 departments")

    # Crime data
    crime_count = _ingest_crime_data(g, nx_graph)
    print(f"  Total crime incidents: {crime_count}")

    # Geographic/facility data
    facility_count = _ingest_geographic_data(g, nx_graph)
    print(f"  Total facilities: {facility_count}")

    # Serialize RDF graph
    serialize_graph(g, RDF_OUTPUT, fmt="turtle")
    print(f"  RDF graph saved to {RDF_OUTPUT}")

    # Graph statistics
    rdf_stats = graph_stats(g)
    nx_stats = {
        "nodes": nx_graph.number_of_nodes(),
        "edges": nx_graph.number_of_edges(),
        "density": round(nx.density(nx_graph), 6) if nx_graph.number_of_nodes() > 0 else 0.0,
        "connected_components": (
            nx.number_weakly_connected_components(nx_graph)
            if nx_graph.number_of_nodes() > 0
            else 0
        ),
    }
    combined_stats = {"rdf": rdf_stats, "networkx": nx_stats}
    STATS_OUTPUT.write_text(json.dumps(combined_stats, indent=2))
    print(f"  Graph stats saved to {STATS_OUTPUT}")

    print(f"\nDone. RDF: {rdf_stats['triples']} triples | "
          f"NX: {nx_stats['nodes']} nodes, {nx_stats['edges']} edges")


if __name__ == "__main__":
    main()
