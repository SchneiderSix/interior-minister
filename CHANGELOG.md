# Changelog

All notable changes to the Interior Minister data pipeline are documented here.

## [0.5.0] - 2026-04-24

### Added
- README.md with full project documentation (architecture, datasets, reproduction steps)

### Changed
- NB06: GNN operates on 19-node department graph (dissolved from 280 seccionales) instead of assuming seccional-level data
- NB06: Temporal train/val split — train on year-pairs (2013→2014 through 2022→2023), validate on 2023→2024
- NB06: Added sklearn scoring: MAE, RMSE, MAPE, R² with per-department prediction table
- NB06: Training curve plot with best epoch marker + predicted vs actual scatter plot
- NB06: 5 data-driven symbolic rules (up from 2 generic rules):
  - Monthly seasonality per crime type (hurto peaks summer, abigeato peaks winter)
  - Hour-of-day risk profile (3x variation: 20h peak vs 3-4h trough)
  - Urban concentration factor (Montevideo 1.2x overrepresentation)
  - DV escalation with CEVDG proximity
  - Crime interaction (hurto surge → rapiña follows)

### Fixed
- NB06: `neural_pred` not defined in cell 10 — changed to `val_pred` from cell 8
- NB06: `escalation_factors` not defined in cell 10 — changed to `symbolic_factors` from cell 9
- NB06: Missing `scikit-learn` in pip install (cell 8 imports sklearn.metrics)

## [0.4.0] - 2026-04-24

### Fixed
- NB04: Z3 verification rewritten from trivial boolean AND to actual symbolic constraint reasoning
  - Phase 1: spec consistency (can any valid row exist under constraints?)
  - Phase 2: data boundary validation (do actual min/max fit the spec?)
  - Phase 3: semantic Python checks (unknown departments, invalid sex values)
- NB04: `ComputeError: cannot compare string with numeric type` — added `_to_numeric()` helper for Polars Utf8→Int64 casting
- NB04: domain knowledge corrected — `sistema_carcelario` year range (2003,2025), added KNOWN_SPECIAL_DEPARTMENTS set, expanded VALID_SEX_VALUES
- NB04: cross-dataset Z3 cell rewritten with symbolic year-overlap constraints
- NB04: `DATA_DIR` not defined — merged GCS download + data loading into single cell
- NB05: `DATA_DIR` not defined — same duplicate cell fix with GCS download
- NB05: Text2SQL prompt rewritten with rich schema info (column types, sample values, explicit column hints)
- NB05: SQL parsing switched from `re.findall` to `re.split` for robust multi-query extraction
- NB06: `DATA_DIR` not defined — same duplicate cell fix with GCS download

## [0.3.0] - 2026-04-24

### Added
- Department normalization function in `schemas.py` (`normalize_department()`) with typo/accent fix map
- Year extraction from `fecha_de_ingreso` in `delitos_sexuales` transform — dataset now has `ano` column (93,438 rows, 2018-2024)
- Jefaturas geographic layer (19 police headquarters, one per department) — ingestion, transform, GCS upload, knowledge graph, NB02

### Fixed
- Department typos across all datasets: `MALDONDADO` → `MALDONADO`, `TACUEREMBO` → `TACUAREMBO`
- Accented department names: `PAYSANDÚ` → `PAYSANDU`, `RÍO NEGRO` → `RIO NEGRO`, `SAN JOSÉ` → `SAN JOSE`, `TACUAREMBÓ` → `TACUAREMBO`
- Mixed-case departments in `medidas_alternativas` (title case → uppercase)
- Applied `normalize_department()` in 7 transforms: delitos, violencia_domestica, delitos_sexuales, homicidios_mujeres, medidas_alternativas, sistema_carcelario (no dept col), geographic
- `delitos_sexuales` was skipped in knowledge graph build due to missing `ano` column — now included

### Changed
- Knowledge graph: 627,376 triples / 125,535 nodes (up from 609K triples, now includes delitos_sexuales + jefaturas)
- NB02: updated for 5 geographic layers (added jefaturas with darkblue/building markers)
- All 13 processed parquet files re-uploaded to GCS with normalized departments

## [0.2.0] - 2026-04-24

### Added
- Custom KML parser in `transform_geographic.py` using `xml.etree` (no Fiona KML driver needed)
- HTML table description parsing for seccionales KML attributes
- Support for Point, Polygon, and MultiGeometry KML geometries

### Fixed
- Geographic ingestion: switched seccionales, comisarias, cevdg to KML format (SHP archives are RAR, not ZIP)
- Comisarias CKAN slug corrected to `tic-ministerio-del-interior-comisarias-uruguay`
- Space-in-URI crash for seccional values in RDF graph (`SECCIONAL 7` → `SECCIONAL_7`)
- SPARQL namespace mismatch in NB03 cells 5-6 (wrong URI and property names)
- SPARQL variable name clash (`?count` → `?total`) causing TypeError
- Column standardization: `año` → `ano` across all schemas, transforms, and notebooks
- Duplicate `nombre` column in seccionales KML parsing

### Changed
- NB01 cell 10: `año` → `ano` in findings summary
- NB02: complete rewrite for 4 geographic layers with multi-layer Folium map
- Knowledge graph column lookups expanded to include `ano`, `depto`, `dpto`, `departamen`, `delito`
- `build_graph.py` crime dataset list updated to match actual parquet filenames

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
