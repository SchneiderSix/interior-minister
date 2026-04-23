# Neuro-Symbolic Architecture Analysis for Interior Ministry Data Pipeline

**Date**: 2026-04-23
**Papers Analyzed**: arXiv:2508.13678 (IJCAI 2025 Survey), arXiv:2601.17789 (NSVIF)
**Data Source**: Uruguay Interior Ministry Open Data Catalog (11 datasets)

---

## 1. Paper Summaries

### Paper 1: Neuro-Symbolic AI -- Towards Improving Reasoning Abilities of LLMs (2508.13678)

**Venue**: IJCAI 2025 Survey Track
**Core thesis**: LLMs excel at pattern recognition (System 1) but fail at deliberate logical reasoning (System 2). Symbolic AI provides the rigor LLMs lack.

**Three Integration Architectures**:

| Direction | Problem Solved | How It Works |
|-----------|---------------|--------------|
| **Symbolic -> LLM** | Data scarcity | Symbolic solvers generate provably correct training data for LLM fine-tuning |
| **LLM -> Symbolic** | Function errors | LLM translates NL to formal representations; symbolic executors (Python/SQL/Z3) guarantee correctness |
| **LLM + Symbolic** | Pipeline losses | Joint optimization with differentiable symbolic modules or symbolic feedback as reward signals |

**Key systems relevant to our pipeline**:
- **Binder**: LLM generates SQL to query tabular data -- directly applicable to CSV government datasets
- **PAL/PoT**: Problems converted to Python code executed via interpreters
- **Tool-Aided**: Pipeline of task planning -> tool selection -> tool calling -> response verification
- **Symbolic Feedback**: Rule-based systems as reward signals in RLHF-style training

**GitHub**: [LAMDASZ-ML/Awesome-LLM-Reasoning-with-NeSy](https://github.com/LAMDASZ-ML/Awesome-LLM-Reasoning-with-NeSy)

---

### Paper 2: NSVIF -- Neuro-Symbolic Verification on Instruction Following (2601.17789)

**Core innovation**: Reformulates verification as a **constraint-satisfaction problem (CSP)** using Z3 SMT solver.

**Three-Agent Pipeline**:

```
[Instruction] -> FORMULATION AGENT -> [Constraints + FOL Formula as Z3 program]
                      |
                      v
              CHECKING AGENT -> classify each constraint as logic or semantic
                |                  |
                Logic -> Python code execution (deterministic)
                Semantic -> LLM-based evaluation (probabilistic)
                      |
                      v
               SOLVER AGENT -> Z3 evaluates composite formula -> SAT/UNSAT + explanation
```

**Results**: 94.8% F1 with GPT-4.1 backend (+25.7pp over LLM-as-judge)

**Constraint taxonomy**:
- **Logic** (symbolically verifiable): ordering, uniqueness, structure/format, required elements, prohibited elements, count, length, pattern
- **Semantic** (neurally evaluated): tone, topic, accuracy, intent alignment

**Killer feature**: Interpretable feedback enables self-correction in 3-5 iterations (vs 15+ with boolean-only feedback)

---

## 2. Data Landscape

### 11 Datasets, Two Categories

**Tabular/Statistical (6)**:
| Dataset | Records | Time Span | Key Entities |
|---------|---------|-----------|-------------|
| Delitos denunciados | >1M | 2013-2025 | Incidents, victims, crime types |
| Violencia domestica | ~47 files | 2020-2024 | DV reports, tobilleras, victims |
| Delitos sexuales | 8 files | 2018-2024 | Sexual crime reports, victims |
| Homicidios a mujeres | 8 files | 2017-2024 | Female homicide victims |
| Medidas alternativas | 12 files | ongoing | Alternative sentences, control methods |
| Sistema carcelario | 36 files | ongoing | Prison population, facilities, demographics |

**Geographic/Spatial (5)**:
| Dataset | Type | Format |
|---------|------|--------|
| Seccionales Policiales | Precinct polygons | SHP/KML |
| Comisarias | Police station points | SHP/KML |
| Jefaturas de Policia | HQ points (19) | SHP/KML |
| Destacamentos Bomberos | Fire station points | SHP/KML |
| CEVDG | DV-specialized stations | SHP/KML |

### Join Keys Across Datasets
- **Departamento** (19 departments) -- universal join key
- **Seccional** (precinct code) -- links crime data to spatial polygons
- **Fecha/Year-Month** -- temporal alignment
- **Sexo** -- demographic dimension
- **Tipo de delito** -- crime classification hierarchy

### Criminal Justice Pipeline (data flow)
```
Reports (Delitos) -> Investigation -> Sentencing -> Prison (Sistema carcelario)
                                                 -> Alternative Measures (Medidas alternativas)
```

### Gender Violence Ecosystem (data flow)
```
DV Reports -> Tobillera monitoring -> Compliance/Violation -> Escalation risk
                                                           -> Sexual violence (Delitos sexuales)
                                                           -> Femicide (Homicidios a mujeres)
```

---

## 3. Proposed Neuro-Symbolic Architecture

Based on both papers and the data landscape, here is the three-layer architecture tailored to this project:

### Layer 1: Symbolic -- Schema & Graph Construction

```
Raw Data (CSV/JSON/SHP/KML)
         |
         v
+----------------------------------+
| SYMBOLIC LAYER 1                 |
|                                  |
| 1. Parse & profile columns       |
|    - types, distributions, nulls |
|    - temporal range validation   |
|    - geographic code validation  |
|                                  |
| 2. Build Knowledge Graph         |
|    - 10 node types, 11 edge types|
|    - Incident -> Person -> Crime |
|    - Location -> Facility -> Area|
|                                  |
| 3. Apply domain ontology         |
|    - Crime classification hierarchy|
|    - Criminal justice pipeline   |
|    - Gender violence escalation  |
|    - Spatial jurisdiction tree   |
|                                  |
| 4. NSVIF-style constraints       |
|    - Schema compliance (logic)   |
|    - Value range checks (logic)  |
|    - Temporal consistency (logic)|
|    - Cross-dataset integrity     |
+----------------------------------+
```

**NSVIF application here**: Each data quality rule becomes a constraint in a Z3 program:
- `FORMAT(date_field) == "YYYY-MM-DD"` (logic constraint -> Python checker)
- `VALUE(departamento) IN valid_departments` (logic constraint -> set membership)
- `COUNT(crime_reports, seccional, month) >= 0` (logic constraint -> range check)
- `CONTENT(crime_classification) MATCHES official_taxonomy` (semantic constraint -> LLM check)

### Layer 2: LLM (Qwen) -- Semantic Bridging

```
+----------------------------------+
| LLM LAYER (Qwen)                |
|                                  |
| 1. Entity linking               |
|    "seccional" <-> "jurisdiccion"|
|    "departamento" <-> geographic |
|    Cross-format field alignment  |
|                                  |
| 2. Relationship inference        |
|    Department + Seccional        |
|      -> spatial hierarchy        |
|    DV report + tobillera         |
|      -> monitoring relationship  |
|    Crime type + sentence         |
|      -> justice pipeline stage   |
|                                  |
| 3. Natural language queries      |
|    Text -> SQL (tabular data)    |
|    Text -> SPARQL (knowledge graph)|
|    Text -> GeoQuery (spatial)    |
|                                  |
| 4. Semantic enrichment           |
|    Classify crime descriptions   |
|    Detect data quality anomalies |
|    Generate metadata annotations |
+----------------------------------+
```

**Paper 2508.13678 patterns applied here**:
- **Program-Aided (PAL/PoT)**: Qwen generates Python/SQL for crime data queries
- **Tool-Aided**: Qwen orchestrates GIS tools, statistical libraries, graph queries
- **Binder pattern**: Direct SQL generation against parquet files in GCS

### Layer 3: Symbolic -- Reasoning & Verification

```
+----------------------------------+
| SYMBOLIC LAYER 2                 |
|                                  |
| 1. Execute queries on graph/DB   |
|    - SPARQL on knowledge graph   |
|    - SQL on parquet (DuckDB/BQ)  |
|    - Spatial queries (PostGIS)   |
|                                  |
| 2. NSVIF constraint checking     |
|    - Formulation: parse data     |
|      quality rules into CSP      |
|    - Checking: logic constraints |
|      via Python, semantic via LLM|
|    - Solver: Z3 evaluates        |
|      composite formula           |
|    - Feedback: interpretable     |
|      error reports               |
|                                  |
| 3. Domain reasoning              |
|    - Temporal logic rules        |
|    - Spatial coverage analysis   |
|    - Escalation pattern detection|
|    - Policy compliance checking  |
|                                  |
| 4. Return verified answers       |
|    - Audit trail (query + result)|
|    - Confidence scoring          |
|    - Constraint satisfaction     |
|      report                      |
+----------------------------------+
```

---

## 4. Concrete Neuro-Symbolic Use Cases (Ranked)

### Tier 1: High Feasibility + High Impact

#### UC-1: Spatio-Temporal Crime Prediction
- **Neural**: GNN on seccional adjacency graph, node features = crime counts + facility density
- **Symbolic**: Temporal logic rules (seasonal patterns, holiday spikes, escalation thresholds)
- **Data**: Delitos denunciados + Seccionales Policiales + facility locations
- **Output**: Hotspot predictions with explainable rule-based justifications

#### UC-2: Data Pipeline Verification (NSVIF-inspired)
- **Neural**: LLM classifies constraint types, generates Python checkers, evaluates semantic constraints
- **Symbolic**: Z3 SMT solver evaluates composite data quality formulas
- **Data**: All 11 datasets (schema validation, cross-dataset integrity)
- **Output**: SAT/UNSAT per dataset load + interpretable violation reports

### Tier 2: Medium Feasibility + Very High Impact

#### UC-3: Gender Violence Escalation Early Warning
- **Neural**: Sequence model on DV report -> tobillera -> escalation trajectory
- **Symbolic**: Legal/procedural rules (repeat offense thresholds, monitoring compliance, risk classification)
- **Data**: Violencia domestica + Homicidios a mujeres + Delitos sexuales
- **Output**: Risk scores with rule-based explanations for intervention prioritization

#### UC-4: Criminal Justice Flow Analysis
- **Neural**: Process mining model learns case flow distributions
- **Symbolic**: Sentencing rules, capacity constraints, recidivism patterns
- **Data**: Delitos denunciados + Sistema carcelario + Medidas alternativas
- **Output**: Bottleneck detection, equity analysis, capacity forecasting

### Tier 3: Exploratory / Research

#### UC-5: Knowledge Graph Embeddings + Rule Learning
- **Neural**: KGE models (TransE/RotatE) on full knowledge graph
- **Symbolic**: ILP discovers interpretable rules from graph structure
- **Data**: All 11 datasets as knowledge graph
- **Output**: Discovered patterns, hypothesis generation

#### UC-6: Anomaly Detection with Causal Reasoning
- **Neural**: Autoencoder on crime time series
- **Symbolic**: Causal Bayesian network (policy changes, economic factors)
- **Data**: All tabular time-series
- **Output**: Anomaly alerts distinguishing genuine trends from expected effects

---

## 5. Architecture Decision: Which Papers Apply Where

| Pipeline Stage | Paper 2508.13678 Pattern | Paper 2601.17789 Pattern |
|----------------|--------------------------|--------------------------|
| **Data ingestion** | -- | Schema constraints as CSP |
| **Data profiling** | Tool-Aided (GIS, stats tools) | Logic constraints (Python checkers) |
| **Entity linking** | LLM -> Symbolic (formalization) | Semantic constraints (LLM evaluation) |
| **Query generation** | Program-Aided (PAL/PoT/Binder) | -- |
| **Query execution** | Symbolic executors (SQL/SPARQL) | -- |
| **Result verification** | Symbolic Feedback | Full NSVIF pipeline (formulate -> check -> solve) |
| **Model training** | Symbolic -> LLM (correct training data) | -- |
| **Prediction explanation** | LLM + Symbolic (symbolic format) | Interpretable constraint reports |

---

## 6. Technology Stack Alignment

| Component | Tool | Role |
|-----------|------|------|
| Pipeline orchestration | **Bruin** | Main pipeline builder and data parser |
| Storage | **GCS (Parquet)** | Column-oriented storage for analytical queries |
| LLM | **Qwen** (neuro-symbolic capable) | Semantic bridging, entity linking, query generation |
| Knowledge Graph | **NetworkX** / **rdflib** | In-memory graph for prototyping |
| Constraint Solver | **Z3 (z3-solver)** | NSVIF-style CSP evaluation |
| Spatial | **GeoPandas** / **Shapely** | SHP/KML processing, spatial joins |
| Notebooks | **Google Colab** | Interactive analysis and model experimentation |
| Query Engine | **DuckDB** | SQL over parquet files |

---

## 7. Data Quality Concerns

1. **Temporal mismatch**: Datasets span different ranges (2013-2025 vs 2020-2024). Cross-dataset analysis must handle this.
2. **Granularity mismatch**: Delitos has microdata (>1M rows); Sistema carcelario is pre-aggregated by year-month.
3. **No person identifiers**: Privacy by design prevents individual tracking across datasets.
4. **Format inconsistency**: Mix of XLS/XLSX/CSV across years needs normalization.
5. **Geographic resolution varies**: Crime data at seccional level; some datasets only at department level.

---

## 8. Next Steps

1. **Set up Bruin pipeline** to ingest all 11 datasets, normalize formats, output to GCS as Parquet
2. **Implement NSVIF-style verification layer** as a Bruin asset for data quality
3. **Build knowledge graph** from normalized data using the proposed ontology
4. **Create Colab notebooks** for each use case tier, starting with UC-1 and UC-2
5. **Select and fine-tune Qwen model** for Spanish-language entity linking and query generation
