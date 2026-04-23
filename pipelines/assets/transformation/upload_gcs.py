""" @bruin
name: transformation.upload_gcs
type: python
tags:
  - transformation
depends:
  - transformation.transform_delitos
  - transformation.transform_violencia_domestica
  - transformation.transform_delitos_sexuales
  - transformation.transform_homicidios_mujeres
  - transformation.transform_medidas_alternativas
  - transformation.transform_sistema_carcelario
  - transformation.transform_geographic
description: Upload all processed Parquet files to Google Cloud Storage
@bruin """

import os
from pathlib import Path

from google.cloud import storage


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DEFAULT_BUCKET = "interior-minister-data-lake-fabled-imagery-488015-p6"


def get_bucket_name() -> str:
    """Get GCS bucket name from environment or use default."""
    return os.environ.get("GCS_BUCKET", DEFAULT_BUCKET)


def upload_directory(
    bucket: storage.Bucket,
    local_dir: Path,
    gcs_prefix: str,
) -> int:
    """Upload all Parquet files from a local directory to GCS.

    Returns the number of files uploaded.
    """
    uploaded = 0
    if not local_dir.exists():
        print(f"Warning: directory not found: {local_dir}")
        return uploaded

    for parquet_file in sorted(local_dir.glob("*.parquet")):
        gcs_path = f"{gcs_prefix}/{parquet_file.name}"
        blob = bucket.blob(gcs_path)
        print(f"Uploading {parquet_file.name} -> gs://{bucket.name}/{gcs_path}")
        blob.upload_from_filename(str(parquet_file))
        uploaded += 1

    return uploaded


def main() -> None:
    bucket_name = get_bucket_name()
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    total_uploaded = 0

    # Upload tabular parquet files
    tabular_dir = PROCESSED_DIR / "tabular"
    total_uploaded += upload_directory(bucket, tabular_dir, "processed/tabular")

    # Upload geographic parquet files
    geographic_dir = PROCESSED_DIR / "geographic"
    total_uploaded += upload_directory(bucket, geographic_dir, "processed/geographic")

    print(f"Upload complete: {total_uploaded} files to gs://{bucket_name}/")


if __name__ == "__main__":
    main()
