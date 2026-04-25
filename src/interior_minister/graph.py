"""Knowledge graph construction helpers using rdflib and NetworkX."""

from __future__ import annotations

from pathlib import Path

import networkx as nx
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

CRIME = Namespace("http://interior-minister.gub.uy/ontology/crime#")
LOC = Namespace("http://interior-minister.gub.uy/ontology/location#")
JUST = Namespace("http://interior-minister.gub.uy/ontology/justice#")


def create_rdf_graph() -> Graph:
    """Create a new RDF graph with bound namespaces."""
    g = Graph()
    g.bind("crime", CRIME)
    g.bind("loc", LOC)
    g.bind("just", JUST)
    return g


def load_ontology(g: Graph, ontology_dir: Path) -> Graph:
    """Load all Turtle ontology files into the graph."""
    for ttl_file in sorted(ontology_dir.glob("*.ttl")):
        g.parse(str(ttl_file), format="turtle")
    return g


def add_incident(
    g: Graph,
    incident_id: str,
    crime_type: str,
    department: str,
    seccional: str | None,
    year: int,
    month: int | None = None,
) -> URIRef:
    """Add a crime incident node to the graph."""
    node = CRIME[f"incident/{incident_id}"]
    g.add((node, RDF.type, CRIME.Incident))
    g.add((node, CRIME.crimeType, Literal(crime_type)))
    g.add((node, CRIME.year, Literal(year, datatype=XSD.integer)))

    if month is not None:
        g.add((node, CRIME.month, Literal(month, datatype=XSD.integer)))

    dept_node = LOC[f"department/{department.replace(' ', '_')}"]
    g.add((node, CRIME.reportedAt, dept_node))

    if seccional:
        secc_node = LOC[f"seccional/{seccional.replace(' ', '_')}"]
        g.add((node, CRIME.reportedAt, secc_node))
        g.add((secc_node, LOC.belongsTo, dept_node))

    return node


def add_facility(
    g: Graph,
    name: str,
    facility_type: str,
    lat: float | None = None,
    lon: float | None = None,
    department: str | None = None,
) -> URIRef:
    """Add a facility (police, fire, prison, CEVDG) to the graph."""
    safe_name = name.replace(" ", "_").replace("/", "_")
    node = LOC[f"facility/{facility_type}/{safe_name}"]
    g.add((node, RDF.type, LOC[f"Facility{facility_type.capitalize()}"]))
    g.add((node, RDFS.label, Literal(name)))

    if lat is not None and lon is not None:
        g.add((node, LOC.latitude, Literal(lat, datatype=XSD.float)))
        g.add((node, LOC.longitude, Literal(lon, datatype=XSD.float)))

    if department:
        dept_node = LOC[f"department/{department.replace(' ', '_')}"]
        g.add((node, LOC.locatedIn, dept_node))

    return node


def add_person(
    g: Graph,
    person_id: str,
    role: str,
    sex: str | None = None,
    incident_uri: URIRef | None = None,
) -> URIRef:
    """Add a person (victim or offender) to the graph."""
    node = CRIME[f"person/{person_id}"]
    g.add((node, RDF.type, CRIME.Person))
    g.add((node, CRIME.role, Literal(role)))

    if sex:
        g.add((node, CRIME.sex, Literal(sex)))

    if incident_uri:
        if role == "victim":
            g.add((node, CRIME.victimOf, incident_uri))
        elif role == "offender":
            g.add((node, CRIME.offenderIn, incident_uri))

    return node


def rdf_to_networkx(rdf_graph: Graph) -> nx.DiGraph:
    """Convert an RDF graph to a NetworkX directed graph for analysis."""
    nx_graph = nx.DiGraph()

    for s, p, o in rdf_graph:
        s_str = str(s)
        p_str = str(p)

        if isinstance(o, URIRef):
            o_str = str(o)
            nx_graph.add_edge(s_str, o_str, predicate=p_str)
        elif isinstance(o, Literal):
            if s_str not in nx_graph:
                nx_graph.add_node(s_str)
            attrs = nx_graph.nodes[s_str]
            prop_name = p_str.split("#")[-1] if "#" in p_str else p_str.split("/")[-1]
            attrs[prop_name] = str(o)

    return nx_graph


def serialize_graph(g: Graph, output_path: Path, fmt: str = "turtle") -> None:
    """Serialize the RDF graph to a file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(str(output_path), format=fmt)


def graph_stats(g: Graph) -> dict:
    """Return basic statistics about the RDF graph."""
    return {
        "triples": len(g),
        "subjects": len(set(g.subjects())),
        "predicates": len(set(g.predicates())),
        "objects": len(set(g.objects())),
    }
