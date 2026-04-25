"""Create BigQuery external tables from GCS Parquet files."""

from pathlib import Path

from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT_ID = "fabled-imagery-488015-p6"
DATASET_ID = "interior_minister"
BUCKET = "interior-minister-data-lake-fabled-imagery-488015-p6"

TABLES = {
    "raw_delitos": "processed/tabular/delitos_denunciados.parquet",
    "raw_violencia_domestica": "processed/tabular/violencia_domestica.parquet",
    "raw_delitos_sexuales": "processed/tabular/delitos_sexuales.parquet",
    "raw_homicidios_mujeres": "processed/tabular/homicidios_mujeres.parquet",
    "raw_medidas_alternativas": "processed/tabular/medidas_alternativas.parquet",
    "raw_sistema_carcelario": "processed/tabular/sistema_carcelario.parquet",
}

def main():
    creds_path = Path(__file__).resolve().parents[1] / "credentials.json"
    if creds_path.exists():
        credentials = service_account.Credentials.from_service_account_file(str(creds_path))
        client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
    else:
        client = bigquery.Client(project=PROJECT_ID)
    for table_name, gcs_path in TABLES.items():
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        source_uri = f"gs://{BUCKET}/{gcs_path}"

        external_config = bigquery.ExternalConfig("PARQUET")
        external_config.source_uris = [source_uri]

        table = bigquery.Table(table_id)
        table.external_data_configuration = external_config

        try:
            client.delete_table(table_id, not_found_ok=True)
            table = client.create_table(table)
            print(f"  OK {table_id} -> {source_uri}")
        except Exception as exc:
            print(f"  FAIL {table_id}: {exc}")

    print("Done creating BigQuery external tables")

if __name__ == "__main__":
    main()
