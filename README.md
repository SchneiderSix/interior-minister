# Uruguay Interior Ministry — Neuro-Symbolic Crime Data Pipeline

End-to-end neuro-symbolic data pipeline for Uruguay's Interior Ministry open data. Combines traditional data engineering with **knowledge graphs**, **formal verification (Z3)**, **LLM-based entity linking (Qwen2.5-7B)**, and **GNN crime prediction** with symbolic rules. Built as a capstone project for the [DataTalksClub Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp).

## Problem Description

Uruguay's Interior Ministry publishes crime and public safety data across multiple open datasets with no unified analytical layer:

- **6 tabular datasets**: Crime reports (delitos denunciados), domestic violence, sexual offenses, femicides, alternative measures, prison system — spanning 2003-2025, 2.4M+ records
- **5 geographic layers**: Police precincts (seccionales), police stations (comisarias), gender violence centers (CEVDG), fire stations (bomberos), police headquarters (jefaturas) — 350+ facilities
- **No cross-dataset linking**: Departments spelled inconsistently, no shared ontology, no entity resolution

This pipeline ingests all 11 datasets, normalizes departments, builds a knowledge graph (627K+ triples), and runs neuro-symbolic analysis notebooks on Google Colab (A100 GPU) to answer questions like:

- What are the spatial diffusion patterns of crime across departments?
- Can we predict next year's crime counts per department using GNN + symbolic rules?
- Do formal constraints (Z3 SMT solver) hold across all datasets?
- Can an LLM generate correct SQL from natural language over crime data?

## Architecture

```
 Data Sources (Interior Ministry Open Data)
 +-----------------+   +---------------------+
 | 6 Tabular CSVs  |   | 5 Geographic Layers |
 | (CKAN API)      |   | (KML / SHP)         |
 +--------+--------+   +---------+-----------+
          |                       |
          v                       v
 +-----------------------------------------------+
 |          Bruin Pipeline (local)                |
 |  ingest -> transform -> verify -> graph        |
 +-------------------+---------------------------+
                     |
                     v
 +-----------------------------------------------+
 |        GCS Data Lake (Parquet)                 |
 |  raw/tabular/    raw/geographic/               |
 |  processed/tabular/  processed/geographic/     |
 |  knowledge_graph/                              |
 +-------------------+---------------------------+
                     |
          +----------+----------+
          |                     |
          v                     v
 +-----------------+   +-------------------+
 | BigQuery        |   | Google Colab      |
 | External Tables |   | (A100 GPU)        |
 +-----------------+   +-------------------+
                       | NB01: Tabular EDA         |
                       | NB02: Geographic EDA      |
                       | NB03: Knowledge Graph     |
                       | NB04: Z3 Verification     |
                       | NB05: Qwen Entity Linking |
                       | NB06: GNN Crime Prediction|
                       +---------------------------+
```

## Technologies Used

| Component | Technology |
|-----------|------------|
| Cloud | Google Cloud Platform (GCS, BigQuery) |
| Infrastructure as Code | Terraform |
| Data Lake | Google Cloud Storage (Parquet format) |
| Data Warehouse | BigQuery (external tables) |
| Batch Processing | Google Colab (A100 GPU) |
| Orchestration | Bruin (DAG pipeline) |
| Transformations | Polars (Python) |
| Knowledge Graph | RDFLib (Turtle format, 627K+ triples) |
| Formal Verification | Z3 SMT Solver (NSVIF-inspired) |
| LLM | Qwen2.5-7B-Instruct (4-bit quantized) |
| GNN | PyTorch Geometric (GCN on department adjacency graph) |
| Geospatial | GeoPandas, Shapely, Folium |

## Datasets

### Tabular (6 datasets, 2.4M+ records)

| Dataset | Records | Years | Description |
|---------|---------|-------|-------------|
| `delitos_denuncias` | 2,423,286 | 2013-2025 | Crime reports (hurto, rapina, abigeato, lesiones, DV) |
| `violencia_domestica` | 196,000+ | 2012-2024 | Domestic violence reports by department |
| `delitos_sexuales` | 93,438 | 2018-2024 | Sexual offense reports |
| `homicidios_mujeres` | 1,200+ | 2018-2024 | Femicides and gender-based homicides |
| `medidas_alternativas` | 5,000+ | 2019-2024 | Alternative justice measures |
| `sistema_carcelario` | 8,000+ | 2003-2025 | Prison population by gender/age |

### Geographic (5 layers, 350+ facilities)

| Layer | Features | Format | Description |
|-------|----------|--------|-------------|
| `seccionales` | 280 | KML (polygons) | Police precinct boundaries |
| `comisarias` | 30 | KML (points) | Police station locations |
| `cevdg` | 19 | KML (points) | Gender violence centers |
| `bomberos` | 24 | SHP (points) | Fire station locations |
| `jefaturas` | 19 | KML (points) | Departmental police HQs |

## Notebooks (Google Colab)

All notebooks run on Google Colab with data downloaded from GCS. Notebooks 04-06 require A100 GPU runtime.

| Notebook | Purpose | Key Output |
|----------|---------|------------|
| `01_eda_tabular` | Exploratory analysis of 6 tabular datasets | Distribution plots, missing data, temporal trends |
| `02_eda_geographic` | Multi-layer geographic visualization | Folium map with 5 layers (seccionales, comisarias, CEVDG, bomberos, jefaturas) |
| `03_knowledge_graph` | SPARQL queries over crime ontology | 627K triples, 125K nodes, cross-dataset queries |
| `04_nsvif_verification` | Z3 formal constraint verification | SAT/UNSAT proofs for schema constraints, data boundaries, cross-dataset consistency |
| `05_qwen_entity_linking` | LLM entity linking + Text2SQL | Qwen2.5-7B generates SQL from natural language, semantic taxonomy evaluation |
| `06_crime_prediction` | GNN + symbolic rules for crime prediction | GCN on 19-dept graph, temporal train/val split, 5 data-driven symbolic rules, R²=0.97 |

## Project Structure

```
interior-minister/
├── terraform/                    # IaC: GCS bucket, BigQuery dataset, service account
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── notebooks/                    # Google Colab notebooks (run on cloud GPU)
│   ├── 01_eda_tabular.ipynb
│   ├── 02_eda_geographic.ipynb
│   ├── 03_knowledge_graph.ipynb
│   ├── 04_nsvif_verification.ipynb
│   ├── 05_qwen_entity_linking.ipynb
│   └── 06_crime_prediction.ipynb
├── pipelines/                    # Bruin pipeline assets
│   ├── pipeline.yml
│   └── assets/
│       ├── ingestion/            # CKAN API + geographic data download
│       ├── transformation/       # Per-dataset Polars transforms + GCS upload
│       ├── quality/              # Schema verification + cross-dataset checks
│       └── knowledge_graph/      # RDF graph builder + export
├── src/interior_minister/        # Shared Python library
│   ├── catalog.py                # CKAN dataset catalog
│   ├── converters.py             # CSV/Excel parsing helpers
│   ├── schemas.py                # Dataset schemas + department normalization
│   ├── constraints.py            # Z3 constraint definitions
│   ├── gcs.py                    # GCS upload/download helpers
│   └── graph.py                  # RDF knowledge graph builder
├── scripts/
│   ├── create_bq_sources.py      # BigQuery external table creation
│   └── inspect_gcs.py            # GCS schema inspection
├── ontology/                     # RDF ontology definitions (Turtle)
│   ├── crime_types.ttl
│   ├── justice_pipeline.ttl
│   └── locations.ttl
├── pyproject.toml                # Python dependencies (all versions pinned)
├── Makefile                      # Reproducibility commands
└── CHANGELOG.md
```

## How to Reproduce

### Prerequisites

- GCP account with billing enabled
- [Terraform](https://www.terraform.io/downloads) >= 1.0
- Python >= 3.11 with [uv](https://docs.astral.sh/uv/)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) authenticated
- Google Colab account (A100 GPU for notebooks 04-06)

### Step 1: Clone and install

```bash
git clone https://github.com/knucklessg1/interior-minister.git
cd interior-minister
uv sync
```

### Step 2: Authenticate with GCP

```bash
make auth
make auth-set-project
```

### Step 3: Provision infrastructure (Terraform)

```bash
cd terraform
# Create terraform.tfvars with: project_id = "your-gcp-project-id"
terraform init
terraform apply
cd ..
```

Creates: GCS bucket, BigQuery dataset `interior_minister`, service account with IAM roles.

### Step 4: Run the pipeline (Bruin)

```bash
make run    # Runs full pipeline: ingest -> transform -> verify -> graph
```

Or run stages individually:

```bash
make ingest      # Download from CKAN API + geographic sources
make transform   # Polars transforms + GCS upload
make verify      # Schema validation + cross-dataset checks
make graph       # Build RDF knowledge graph (627K+ triples)
```

### Step 5: Create BigQuery external tables

```bash
make bq-create-sources
```

### Step 6: Run notebooks (Google Colab)

Upload notebooks to Google Colab and run in order (01-06). Each notebook downloads its data from GCS automatically.

### Quick reference (Makefile)

```bash
make setup            # uv sync --group dev
make audit            # pip-audit security check
make infra            # terraform apply
make run              # full pipeline
make bq-create-sources # BigQuery external tables
make clean            # remove local data
make destroy          # terraform destroy
```

## Cleanup

```bash
make destroy    # Removes GCS bucket and BigQuery dataset
make clean      # Removes local data directories
```
