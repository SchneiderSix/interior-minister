# Changelog

All notable changes to the Interior Minister data pipeline are documented here.

## [0.1.0] - 2026-04-23

### Added
- Project scaffolding: directory structure, .gitignore, pyproject.toml, Makefile
- Terraform infrastructure: GCS bucket, BigQuery dataset, service account
- Bruin pipeline configuration and asset structure
- Shared Python library: catalog, converters, GCS helpers, schemas, constraints, graph
- Ingestion assets for 6 tabular and 5 geographic datasets
- Transformation assets with per-dataset normalization
- NSVIF-inspired verification layer with Z3 constraint solver
- Knowledge graph builder with crime domain ontology (Turtle format)
- BigQuery external table creation scripts
- 6 Google Colab notebooks for EDA, verification, and neuro-symbolic analysis
