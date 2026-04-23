# Uruguay Interior Ministry Open Data Catalog - Comprehensive Analysis

**Source**: [Ministerio del Interior - Catalogo de Datos Abiertos](https://catalogodatos.gub.uy/organization/tic-ministerio-del-interior)
**Date of Analysis**: 2026-04-23
**Total Datasets**: 11 (across 3 pages)

---

## Part 1: Complete Dataset Catalog

### Dataset 1: Delitos denunciados en el Uruguay
- **URL**: https://catalogodatos.gub.uy/dataset/ministerio-del-interior-delitos_denunciados_en_el_uruguay
- **Description**: Microdata on intentional homicides and reports of robberies (rapinas), injuries (lesiones), domestic violence, theft (hurto), and cattle rustling (abigeato), extracted from the Public Security Management System (SGSP).
- **Formats**: XLSX, CSV, XML, JSON (metadata), eBook (methodological note)
- **Time Period**: January 2013 - Q4 2025 (quarterly updates)
- **Geographic Scope**: National territory
- **Update Frequency**: Quarterly (trimestral)
- **Resources**:
  - Homicidios dolosos consumados (XLSX, CSV, XML) - victim-level data
  - Metadatos de homicidios dolosos consumados (JSON)
  - Denuncias de otros delitos (CSV) - >1 million records
  - Metadatos de denuncias de otros delitos (JSON)
  - Nota metodologica (eBook)
- **Key Fields**: Temporal variables, geographic location, apparent motive, weapon type, judicial intervention, demographic characteristics of victims, aggressor relationship
- **Tags**: Delitos denunciados, Denuncias de abigeatos/hurtos/lesiones/rapina/violencia domestica, Homicidios dolosos consumados
- **Categories**: Seguridad Ciudadana, Violencia

---

### Dataset 2: Violencia domestica y asociados
- **URL**: https://catalogodatos.gub.uy/dataset/violencia-domestica-y-asociados
- **Description**: Data from SGSP on domestic violence situations and the electronic ankle bracelet monitoring program. Published by the Direccion Nacional de Politicas de Genero.
- **Formats**: XLSX, XLS, CSV, XML, JSON (metadata)
- **Time Period**: 2020-2024 (annual files per year)
- **Geographic Scope**: National, with departmental breakdowns
- **Update Frequency**: Annual
- **Resources**: 47 total files organized by year and type:
  - Denuncias de violencia domestica y asociados (per year 2021-2024) - reports
  - Victimas de violencia domestica y asociados (per year 2020-2024) - victim data
  - Tobilleras electronicas program data (3 files): cases by department, victim/offender by sex, relationship type
  - Metadata files (JSON) for each data category
- **Key Fields**: Report date, crime classification (titulo), jurisdiction, department, victim sex, offender sex, birth date, victim-offender relationship type
- **Tags**: 5toPlanGA, Seguridad publica, Tobilleras, Violencia domestica
- **Categories**: Estadisticas, Seguridad Ciudadana, Violencia

---

### Dataset 3: Delitos sexuales
- **URL**: https://catalogodatos.gub.uy/dataset/delitos-sexuales
- **Description**: Data from SGSP on major sexual crimes reported. Published by the Direccion Nacional de Politicas de Genero.
- **Formats**: JSON (metadata), XML, XLSX, CSV
- **Time Period**: 2018-2024
- **Geographic Scope**: National, with departmental breakdowns
- **Update Frequency**: Annual
- **Resources**: 8 files
  - Denuncias de delitos sexuales (XML, XLSX, CSV) - reported incidents
  - Metadatos de denuncias de delitos sexuales (JSON)
  - Victimas de delitos sexuales (XML, XLSX, CSV) - victim-level data
  - Metadatos de victimas de delitos sexuales (JSON)
- **Key Fields**: Report date, offense classification, jurisdiction, department, victim sex, victim birth date
- **Crime Categories**: Sexual abuse (three criminal variants), violent indecent assault, rape
- **Tags**: 5toPlanGA, Abuso sexual, Delitos sexuales, Genero, Seguridad Publica, Violencia sexual
- **Categories**: Estadisticas, Seguridad Ciudadana, Violencia

---

### Dataset 4: Homicidios a mujeres
- **URL**: https://catalogodatos.gub.uy/dataset/homicidios-a-mujeres
- **Description**: Data on homicides against women, covering both domestic homicides and gender-based violence homicides (femicides). Published by the Direccion Nacional de Politicas de Genero.
- **Formats**: JSON (metadata), XML, XLSX, CSV
- **Time Period**: 2017-2024
- **Geographic Scope**: National
- **Update Frequency**: Annual
- **Resources**: 8 files
  - Homicidios domesticos (JSON metadata, XML, XLSX, CSV) - domestic context
  - Homicidios por violencia basada en genero (JSON metadata, XML, XLSX, CSV) - femicidal context
- **Key Fields**: Victim-perpetrator relationship (partner, ex-partner, family, affective-sexual), temporal data, location
- **Tags**: Femicidios, Feminicidios, Genero, Homicidios a mujeres, Violencia basada en genero, Violencia domestica, 5toPlanGA
- **Categories**: Estadisticas, Seguridad Ciudadana, Violencia

---

### Dataset 5: Medidas alternativas
- **URL**: https://catalogodatos.gub.uy/dataset/ministerio-del-interior-medidas-alternativas
- **Description**: Data on evolution of different types of alternative measures to incarceration, geographic distribution, control methods, and gender of affected population.
- **Formats**: JSON (metadata), XML, CSV, XLSX
- **Time Period**: Aggregated by year and month (ongoing)
- **Geographic Scope**: National, with departmental breakdowns
- **Update Frequency**: Quarterly (trimestral)
- **Resources**: 12 files in 3 groups:
  - Tipos de medidas alternativas (JSON, XML, CSV, XLSX) - measure types over time
  - Tipos de medidas alternativas por departamento (JSON, XML, CSV, XLSX) - geographic
  - Medios de control de medidas alternativas segun genero (JSON, XML, CSV, XLSX) - control methods by gender
- **Key Fields**: Year, month, measure type, department, control method, gender
- **Measure Types**: Arrestos domiciliarios, cautelares, libertades a prueba, libertades vigiladas, prision domiciliaria, suspensiones condicionales del proceso, tareas comunitarias
- **Tags**: Arrestos domiciliarios, Cautelares, Libertades a prueba/vigiladas, Prision domiciliaria, Sistema carcelario, Suspensiones condic, Tareas comunitarias
- **Categories**: Seguridad Ciudadana, Transparencia, Violencia

---

### Dataset 6: Sistema carcelario
- **URL**: https://catalogodatos.gub.uy/dataset/ministerio-del-interior-sistema-carcelario
- **Description**: Evolution and characteristics of the incarcerated population (PPL) in facilities belonging to the Instituto Nacional de Rehabilitacion.
- **Formats**: JSON (metadata), XML, CSV, XLSX
- **Time Period**: Aggregated by year and month (ongoing)
- **Geographic Scope**: National, by penitentiary facility
- **Update Frequency**: Quarterly (trimestral)
- **Resources**: 36 files in 7 groups:
  - PPL por delito, sexo y grupos de edad - by crime, sex, age group
  - PPL por establecimiento penitenciario, sexo y edad - by facility, sex, age
  - Fugas - escapes by location
  - Genero y diversidad - pregnant women, mothers with children, minors, transgender persons
  - PPL por nacionalidad, sexo y edad - by nationality, sex, age
  - Poblacion PPL por sexo - total population by sex
  - Suicidios de PPL - completed suicides
- **Key Fields**: Year, month, crime type, sex, age group, facility name, nationality, escape location
- **Tags**: Fugas, Genero y diversidad en PPL, PPL, PPL por Establecimientos Penitenciarios, PPL por edad/nacionalidad/sexo, Poblacion privada de libertad, Sistema carcelario, Suicidios de PPL
- **Categories**: Seguridad Ciudadana, Transparencia, Violencia

---

### Dataset 7: Seccionales Policiales
- **URL**: https://catalogodatos.gub.uy/dataset/tic-ministerio-del-interior-seccionales-policiales
- **Description**: Police precinct boundaries covering all national territory. Excludes coastal zones and water bodies under naval jurisdiction.
- **Formats**: SHP, KML, ODS (metadata)
- **Time Period**: 2020 (single publication)
- **Geographic Scope**: National territory (excluding maritime areas)
- **Update Frequency**: Single publication
- **Spatial Reference**: WGS 84/UTM zone 21S
- **Version**: 3.2
- **Tags**: Ministerio del Interior, Seccionales policiales, Seguridad ciudadana, Uruguay
- **Categories**: Seguridad Ciudadana

---

### Dataset 8: Destacamentos de Bomberos
- **URL**: https://catalogodatos.gub.uy/dataset/tic-ministerio-del-interior-destacamentos-d-n-b
- **Description**: Locations of the National Fire Department (Direccion Nacional de Bomberos) outposts.
- **Formats**: SHP, KML, ODS (metadata)
- **Time Period**: Single publication (created 2018)
- **Geographic Scope**: National
- **Update Frequency**: Single publication
- **Tags**: Destacamentos, Transparencia
- **Categories**: Geograficos, Infraestructura

---

### Dataset 9: Jefaturas de Policia
- **URL**: https://catalogodatos.gub.uy/dataset/tic-ministerio-del-interior-jefaturas
- **Description**: Locations of Police Headquarters for all 19 departments of Uruguay.
- **Formats**: RAR (shapefile archive), KML, ODS (metadata)
- **Time Period**: 2020 (single publication)
- **Geographic Scope**: 19 departments
- **Spatial Reference**: WGS 84/UTM zone 21S
- **Update Frequency**: Single publication
- **Tags**: Jefaturas, Ministerio del Interior, Seguridad Ciudadana
- **Categories**: Seguridad Ciudadana

---

### Dataset 10: Comisarias
- **URL**: https://catalogodatos.gub.uy/dataset/comisarias (inferred)
- **Description**: Locations of police stations (comisarias) throughout national territory. Version 1.1 added Comisarias 29 and 30 of Canelones (02/04/2020).
- **Formats**: SHP, KML, ODS (metadata)
- **Time Period**: 2020 (version 1.1)
- **Geographic Scope**: National territory
- **Update Frequency**: Single publication
- **Tags**: Comisarias, Jefaturas, Ministerio del Interior, Uruguay
- **Categories**: Seguridad Ciudadana

---

### Dataset 11: Ubicacion de las Comisarias Especializadas en Violencia Domestica y Genero (CEVDG)
- **URL**: https://catalogodatos.gub.uy/dataset/tic-ministerio-del-interior-uevdg
- **Description**: Locations of specialized police stations for domestic violence and gender-based violence cases.
- **Formats**: SHP, KML, ODS (metadata)
- **Time Period**: Single publication (last updated Jan 2024)
- **Geographic Scope**: National
- **Update Frequency**: Single publication
- **Tags**: Unidad especializada, Violencia, Violencia basada en genero, Violencia domestica
- **Categories**: Desarrollo Social

---

## Part 2: Duplicate and Format Analysis

### Multi-Format Duplicates (Same Data, Different Serializations)

Almost every tabular dataset provides the identical data in multiple formats. These are NOT separate datasets but the same content serialized differently:

| Dataset | Formats Available | Primary Data Format |
|---------|-------------------|---------------------|
| Delitos denunciados | XLSX, CSV, XML, JSON (meta) | CSV (>1M records) |
| Violencia domestica | XLSX, XLS, CSV, XML, JSON (meta) | CSV/XLSX per year |
| Delitos sexuales | XLSX, CSV, XML, JSON (meta) | CSV |
| Homicidios a mujeres | XLSX, CSV, XML, JSON (meta) | CSV |
| Medidas alternativas | XLSX, CSV, XML, JSON (meta) | CSV |
| Sistema carcelario | XLSX, CSV, XML, JSON (meta) | CSV |

All geographic datasets provide:

| Dataset | Formats Available |
|---------|-------------------|
| Seccionales Policiales | SHP, KML, ODS (meta) |
| Destacamentos Bomberos | SHP, KML, ODS (meta) |
| Jefaturas de Policia | RAR (SHP), KML, ODS (meta) |
| Comisarias | SHP, KML, ODS (meta) |
| CEVDG | SHP, KML, ODS (meta) |

### Content-Level Overlaps

1. **Domestic violence appears in THREE datasets**:
   - `Delitos denunciados` includes domestic violence as one crime type among many (2013-2025)
   - `Violencia domestica y asociados` provides dedicated, more detailed DV data (2020-2024)
   - `Homicidios a mujeres` covers lethal DV outcomes specifically (2017-2024)

2. **Homicide data appears in TWO datasets**:
   - `Delitos denunciados` contains all intentional homicides (homicidios dolosos consumados)
   - `Homicidios a mujeres` contains the female-victim subset with gender-specific context

3. **Sexual crimes may overlap with "delitos denunciados"**: The main crimes dataset covers "lesiones" which can overlap with sexual assault in some classifications.

4. **Alternative measures and prison system are complementary**: Medidas alternativas tracks people NOT in prison; Sistema carcelario tracks those IN prison. Together they represent the full post-sentencing population.

---

## Part 3: Entity Type Analysis

### Core Entity Types Across Datasets

| Entity Type | Datasets Where Present | Attributes |
|-------------|----------------------|------------|
| **Incident/Report** | Delitos, VD, Delitos sexuales, Homicidios | Date, classification, jurisdiction, department |
| **Victim** | Delitos, VD, Delitos sexuales, Homicidios a mujeres | Sex, birth date, relationship to offender |
| **Offender/Aggressor** | VD (tobilleras), Homicidios a mujeres | Sex, relationship to victim |
| **Location (Department)** | ALL tabular datasets | 19 departments of Uruguay |
| **Location (Jurisdiction/Seccional)** | Delitos, VD, Delitos sexuales | Police precinct code |
| **Crime Type** | Delitos, VD, Delitos sexuales, Sistema carcelario | Criminal classification hierarchy |
| **Date/Time** | ALL tabular datasets | Year, month, quarter, specific date |
| **Facility (Penitentiary)** | Sistema carcelario | Facility name, location |
| **Facility (Police)** | Seccionales, Comisarias, Jefaturas, CEVDG | Geographic coordinates, jurisdiction |
| **Facility (Fire)** | Destacamentos Bomberos | Geographic coordinates |
| **Alternative Measure** | Medidas alternativas | Type, control method, department, gender |
| **Monitored Person** | VD (tobilleras), Medidas alternativas | Gender, department, relationship |
| **Spatial Polygon** | Seccionales Policiales | Precinct boundary geometry |
| **Spatial Point** | Bomberos, Jefaturas, Comisarias, CEVDG | Lat/lon coordinates |

### Shared Dimensions (Join Keys)

| Dimension | Type | Appears In |
|-----------|------|------------|
| **Departamento** | Categorical (19 values) | ALL datasets |
| **Seccional/Jurisdiccion** | Categorical | Delitos, VD, Delitos sexuales + Seccionales SHP |
| **Fecha** (Date) | Temporal | ALL tabular datasets |
| **Sexo** (Sex) | Categorical (M/F) | VD, Delitos sexuales, Homicidios, Sistema carcelario, Medidas alternativas |
| **Tipo de delito** (Crime type) | Categorical hierarchy | Delitos, Delitos sexuales, Sistema carcelario |
| **Year-Month** | Temporal | Sistema carcelario, Medidas alternativas |

---

## Part 4: Inter-Dataset Relationships

### Direct Relationships (Linkable via Shared Keys)

```
Delitos denunciados ──(departamento, fecha)──> Seccionales Policiales [spatial join]
                    ──(crime_type overlap)───> Sistema carcelario
                    ──(DV subset)───────────> Violencia domestica y asociados
                    ──(homicide subset)─────> Homicidios a mujeres

Violencia domestica ──(genero-violencia)────> CEVDG locations [spatial context]
                    ──(tobilleras program)──> Medidas alternativas [monitoring overlap]
                    ──(lethal outcomes)─────> Homicidios a mujeres

Delitos sexuales ───(departamento, fecha)──> Seccionales Policiales [spatial join]
                 ───(victim demographics)──> Violencia domestica [co-occurrence]

Sistema carcelario ──(inverse flow)────────> Medidas alternativas [full corrections pop.]
                   ──(crime → sentence)────> Delitos denunciados [pipeline]

Seccionales Policiales ──(contains)────────> Comisarias [point-in-polygon]
                       ──(contains)────────> CEVDG [point-in-polygon]
                       ──(contains)────────> Jefaturas [point-in-polygon]

All geographic ────────(departamento)──────> ALL tabular datasets
```

### Inferred Analytical Relationships

1. **Criminal Justice Pipeline**: Report (Delitos) -> Investigation -> Sentencing -> Prison (Sistema carcelario) OR Alternative Measures (Medidas alternativas)

2. **Gender Violence Ecosystem**: DV Reports (Violencia domestica) -> Electronic monitoring (Tobilleras) -> Escalation to lethal violence (Homicidios a mujeres) or Sexual violence (Delitos sexuales)

3. **Spatial-Temporal Correlation**: Crime incident data (all tabular) can be joined to police precinct boundaries (Seccionales) to compute crime density per precinct, response coverage areas, and resource allocation analysis.

4. **Population Flows**: Prison population (Sistema carcelario) + Alternative measures population = total corrections population. Inflows come from crime reports; outflows are releases.

---

## Part 5: Knowledge Graph Structure

### Proposed Ontology

```
                          ┌─────────────┐
                          │   INCIDENT   │
                          │ (Report/Case)│
                          └──────┬───────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
     ┌──────▼──────┐    ┌───────▼──────┐    ┌───────▼───────┐
     │   PERSON    │    │   LOCATION   │    │  CRIME_TYPE   │
     │(Victim/     │    │(Department/  │    │(Classification│
     │ Offender)   │    │ Seccional)   │    │  hierarchy)   │
     └──────┬──────┘    └───────┬──────┘    └───────┬───────┘
            │                   │                    │
            │            ┌──────▼──────┐             │
            │            │  FACILITY   │             │
            │            │(Police/Fire/│             │
            │            │ Prison/CEVDG)│            │
            │            └─────────────┘             │
            │                                        │
     ┌──────▼──────┐                         ┌───────▼───────┐
     │   MEASURE   │                         │   SENTENCE    │
     │(Alternative/│                         │(Incarceration/│
     │ Monitoring) │                         │ Alt. measure) │
     └─────────────┘                         └───────────────┘
```

### Node Types

| Node | Properties | Source Datasets |
|------|------------|-----------------|
| `Incident` | id, date, type, classification, jurisdiction | Delitos, VD, Delitos sexuales |
| `Person` | role (victim/offender), sex, birth_date, nationality | VD, Delitos sexuales, Homicidios, Sistema carcelario |
| `Location::Department` | name, code (1-19) | ALL |
| `Location::Seccional` | code, geometry (polygon) | Seccionales Policiales |
| `Facility::Police` | name, type, coordinates | Comisarias, Jefaturas, CEVDG |
| `Facility::Fire` | name, coordinates | Destacamentos Bomberos |
| `Facility::Prison` | name, location | Sistema carcelario |
| `CrimeType` | code, label, category | Delitos, Sistema carcelario |
| `Measure` | type, control_method, start_date | Medidas alternativas |
| `MonitoringProgram` | type (tobillera), status | VD (tobilleras) |
| `TimePeriod` | year, month, quarter | ALL |

### Edge Types

| Edge | From | To | Properties |
|------|------|----|------------|
| `REPORTED_AT` | Incident | Location | date |
| `VICTIM_OF` | Person | Incident | relationship_to_offender |
| `OFFENDER_IN` | Person | Incident | relationship_to_victim |
| `CLASSIFIED_AS` | Incident | CrimeType | |
| `LOCATED_IN` | Facility | Location::Seccional | |
| `BELONGS_TO` | Location::Seccional | Location::Department | |
| `SENTENCED_TO` | Person | Facility::Prison | crime, date |
| `ASSIGNED_MEASURE` | Person | Measure | type, date |
| `MONITORED_BY` | Person | MonitoringProgram | status |
| `ESCALATED_TO` | Incident (DV) | Incident (Homicide) | inferred |
| `SERVES_AREA` | Facility | Location::Seccional | jurisdiction |

### Triple Examples

```
(Incident_12345) -[CLASSIFIED_AS]-> (CrimeType:Rapina)
(Incident_12345) -[REPORTED_AT]-> (Seccional:Montevideo_3ra)
(Seccional:Montevideo_3ra) -[BELONGS_TO]-> (Department:Montevideo)
(Victim_A) -[VICTIM_OF]-> (Incident_12345)
(Comisaria_29) -[LOCATED_IN]-> (Seccional:Canelones_5ta)
(Person_B) -[SENTENCED_TO]-> (Prison:Libertad)
(Person_B) -[ASSIGNED_MEASURE]-> (Measure:ArrestoDomiciliario)
```

---

## Part 6: Neuro-Symbolic Approaches

### 1. Spatio-Temporal Crime Prediction (Highest Value)

**Approach**: Graph Neural Networks (GNN) on the spatial graph + symbolic temporal rules

- **Neural component**: A GNN operates over the seccional polygon adjacency graph, learning spatial crime diffusion patterns. Node features include crime counts by type, demographic indicators, and facility density (police stations, CEVDG).
- **Symbolic component**: Temporal logic rules encode known patterns:
  - `IF crime_rate(seccional, month) > threshold AND adjacent_seccional_rate > threshold THEN hotspot_risk = HIGH`
  - Calendar-based rules (seasonal effects, holiday spikes)
  - Escalation rules: `IF DV_reports(area, t) increasing AND no_CEVDG_nearby THEN femicide_risk elevated`
- **Data sources**: Delitos denunciados + Seccionales Policiales + all facility locations
- **Value**: Resource allocation, patrol optimization, preventive deployment

### 2. Gender Violence Escalation Modeling

**Approach**: Neurosymbolic event sequence modeling

- **Neural component**: Sequence model (transformer or LSTM) trained on the temporal progression within the gender violence ecosystem: DV report -> repeated DV -> tobillera assignment -> compliance/violation -> potential escalation to sexual violence or homicide.
- **Symbolic component**: Legal/procedural rules as hard constraints:
  - `IF tobillera_assigned(person) AND violation_detected THEN escalation_protocol`
  - `IF DV_report_count(victim, 12months) >= 3 THEN high_risk_classification`
  - Relationship ontology: partner > ex-partner > family (risk weighting)
- **Data sources**: Violencia domestica (including tobilleras) + Homicidios a mujeres + Delitos sexuales
- **Value**: Early warning system for lethal violence risk, intervention prioritization

### 3. Criminal Justice Flow Analysis

**Approach**: Neural process mining + symbolic constraint satisfaction

- **Neural component**: A neural process model learns the empirical distribution of case flows from crime report to final disposition (prison or alternative measure). Detects bottlenecks, anomalous case durations, and systemic biases.
- **Symbolic component**: Legal framework as constraints:
  - Sentencing rules: `crime_type(X) AND severity(X) >= threshold -> eligible_measures(X, [prison, domiciliario])`
  - Capacity constraints: `IF prison_pop(facility) >= capacity THEN prefer_alternative_measures`
  - Recidivism rules linking prior crimes to current risk assessment
- **Data sources**: Delitos denunciados + Sistema carcelario + Medidas alternativas
- **Value**: Policy evaluation, sentencing equity analysis, capacity planning

### 4. Spatial Coverage Optimization

**Approach**: Differentiable optimization with symbolic geographic constraints

- **Neural component**: A neural network learns the relationship between facility placement (police stations, CEVDG, fire stations) and service quality metrics (response time proxy via distance, crime clearance rates, DV report accessibility).
- **Symbolic component**: Hard geographic and institutional constraints:
  - `EVERY department MUST have >= 1 jefatura` (already satisfied)
  - `CEVDG coverage: max_distance(any_point_in_seccional, nearest_CEVDG) < threshold`
  - Jurisdictional boundaries as inviolable constraints
  - Budget constraints on new facility placement
- **Data sources**: All 5 geographic datasets + crime density from tabular data
- **Value**: Identifying underserved areas, optimal placement of new CEVDG stations

### 5. Knowledge Graph Embedding + Rule Learning

**Approach**: Knowledge graph embeddings (KGE) with inductive logic programming (ILP)

- **Neural component**: Train KGE models (TransE, RotatE, or CompGCN) on the full knowledge graph to learn dense entity representations. These embeddings capture latent relationships not explicit in the data.
- **Symbolic component**: ILP discovers interpretable rules from the graph:
  - `high_dv_rate(X) AND low_cevdg_density(X) -> underserved(X)` (discovered rule)
  - `crime_type(rapina) AND location(X) AND time(night) -> pattern(X, night_robbery)` (discovered)
  - Rules are validated against domain expert knowledge
- **Data sources**: Full knowledge graph built from all 11 datasets
- **Value**: Hypothesis generation, pattern discovery, explainable predictions

### 6. Anomaly Detection with Causal Reasoning

**Approach**: Neural anomaly detection + symbolic causal graphs

- **Neural component**: Autoencoder or variational model trained on normal crime/corrections patterns to detect statistical anomalies (sudden spikes, unusual distributions).
- **Symbolic component**: Causal Bayesian network encoding known causal chains:
  - Economic downturn -> property crime increase
  - Policy change (e.g., new DV law) -> reporting rate change (not necessarily crime change)
  - Prison overcrowding -> increased alternative measures
  - Distinguishes genuine anomalies from expected effects of known causes
- **Data sources**: All tabular time-series datasets
- **Value**: Early detection of emerging crime trends, policy impact evaluation

### Priority Ranking

| Rank | Approach | Feasibility | Impact | Data Readiness |
|------|----------|-------------|--------|----------------|
| 1 | Spatio-temporal crime prediction | HIGH | HIGH | HIGH |
| 2 | Gender violence escalation | MEDIUM | VERY HIGH | MEDIUM |
| 3 | Knowledge graph embeddings | HIGH | MEDIUM | HIGH |
| 4 | Criminal justice flow | MEDIUM | HIGH | MEDIUM |
| 5 | Spatial coverage optimization | HIGH | MEDIUM | HIGH |
| 6 | Anomaly detection + causal | MEDIUM | MEDIUM | HIGH |

---

## Part 7: Data Quality Observations

1. **Temporal inconsistency**: Datasets cover different time ranges (2013-2025 for delitos vs 2017-2024 for homicidios a mujeres vs 2020-2024 for violencia domestica). Any cross-dataset analysis must account for this.

2. **Granularity mismatch**: Delitos denunciados has incident-level microdata (>1M records); Sistema carcelario and Medidas alternativas are pre-aggregated by year-month. This limits join precision.

3. **No unique person identifiers**: There is no way to track individuals across datasets (by design, for privacy). This prevents direct linkage of a DV victim to a homicide victim record.

4. **Geographic resolution varies**: Crime data has seccional-level resolution; geographic datasets have point/polygon geometries. The link is the seccional code, which should be consistent but needs validation.

5. **Format standardization needed**: The violencia domestica dataset uses both XLS and XLSX across years, and some years lack CSV versions. Normalization would be required before bulk processing.

6. **Metadata quality is good**: JSON metadata files accompany each data resource, providing field descriptions. The eBook methodological note for delitos denunciados is a valuable reference.
