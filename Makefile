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
	USERPROFILE="$(HOME)" bruin run --tag ingestion pipelines/

transform:
	USERPROFILE="$(HOME)" bruin run --tag transformation pipelines/

verify:
	USERPROFILE="$(HOME)" bruin run --tag quality pipelines/

graph:
	USERPROFILE="$(HOME)" bruin run --tag knowledge_graph pipelines/

run:
	USERPROFILE="$(HOME)" bruin run pipelines/

# --- BigQuery ---

bq-create-sources:
	uv run python scripts/create_bq_sources.py

bq-tables:
	uv run python -c "from google.cloud import bigquery; from google.oauth2 import service_account; \
		creds = service_account.Credentials.from_service_account_file('credentials.json'); \
		c = bigquery.Client(project='$(GCP_PROJECT_ID)', credentials=creds); \
		[print(t.table_id) for t in c.list_tables('$(GCP_PROJECT_ID).interior_minister')]"

clean:
	rm -rf data/raw data/processed
	mkdir -p data/raw/tabular data/raw/geographic data/processed/tabular data/processed/geographic
