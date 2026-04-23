.PHONY: setup audit auth auth-set-project auth-service-account infra destroy \
       ingest transform verify graph run bq-create-sources bq-tables clean

TERRAFORM := "C:/Program Files/ProjectsCode/terraform.exe"
GCLOUD    := "C:/Program Files/ProjectsCode/google-cloud-sdk/bin/gcloud.cmd"
BQ        := "C:/Program Files/ProjectsCode/google-cloud-sdk/bin/bq.cmd"

GCP_PROJECT_ID := fabled-imagery-488015-p6
BUCKET := interior-minister-data-lake-$(GCP_PROJECT_ID)

# --- Setup ---

setup:
	uv sync --group dev

audit:
	uv run pip-audit

# --- GCP Authentication ---

auth:
	$(GCLOUD) auth login
	$(GCLOUD) auth application-default login

auth-set-project:
	$(GCLOUD) config set project $(GCP_PROJECT_ID)

auth-service-account:
	$(GCLOUD) iam service-accounts keys create credentials.json \
		--iam-account=interior-minister-pipeline@$(GCP_PROJECT_ID).iam.gserviceaccount.com

# --- Infrastructure ---

infra:
	cd terraform && $(TERRAFORM) init && $(TERRAFORM) apply -auto-approve

destroy:
	cd terraform && $(TERRAFORM) destroy -auto-approve

# --- Pipeline Stages ---

ingest:
	bruin run --tag ingestion pipelines/

transform:
	bruin run --tag transformation pipelines/

verify:
	bruin run --tag quality pipelines/

graph:
	bruin run --tag knowledge_graph pipelines/

run:
	bruin run pipelines/

# --- BigQuery ---

bq-create-sources:
	$(BQ) mk --external_table_definition='gs://$(BUCKET)/processed/tabular/delitos_denunciados.parquet@PARQUET' \
		$(GCP_PROJECT_ID):interior_minister.raw_delitos || true
	$(BQ) mk --external_table_definition='gs://$(BUCKET)/processed/tabular/violencia_domestica.parquet@PARQUET' \
		$(GCP_PROJECT_ID):interior_minister.raw_violencia_domestica || true
	$(BQ) mk --external_table_definition='gs://$(BUCKET)/processed/tabular/delitos_sexuales.parquet@PARQUET' \
		$(GCP_PROJECT_ID):interior_minister.raw_delitos_sexuales || true
	$(BQ) mk --external_table_definition='gs://$(BUCKET)/processed/tabular/homicidios_mujeres.parquet@PARQUET' \
		$(GCP_PROJECT_ID):interior_minister.raw_homicidios_mujeres || true
	$(BQ) mk --external_table_definition='gs://$(BUCKET)/processed/tabular/medidas_alternativas.parquet@PARQUET' \
		$(GCP_PROJECT_ID):interior_minister.raw_medidas_alternativas || true
	$(BQ) mk --external_table_definition='gs://$(BUCKET)/processed/tabular/sistema_carcelario.parquet@PARQUET' \
		$(GCP_PROJECT_ID):interior_minister.raw_sistema_carcelario || true
	@echo "Source tables created in BigQuery"

bq-tables:
	$(BQ) ls $(GCP_PROJECT_ID):interior_minister

clean:
	rm -rf data/raw data/processed
	mkdir -p data/raw/tabular data/raw/geographic data/processed/tabular data/processed/geographic
