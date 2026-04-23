"""GCS upload helpers."""

from __future__ import annotations

import os
from pathlib import Path

from google.cloud import storage

DEFAULT_BUCKET = os.environ.get(
    "GCS_BUCKET", "interior-minister-data-lake-fabled-imagery-488015-p6"
)


def get_client() -> storage.Client:
    """Create a GCS client using application default credentials."""
    return storage.Client()


def upload_file(
    local_path: Path,
    gcs_prefix: str,
    bucket_name: str = DEFAULT_BUCKET,
) -> str:
    """Upload a local file to GCS. Returns the gs:// URI."""
    client = get_client()
    bucket = client.bucket(bucket_name)
    blob_name = f"{gcs_prefix}/{local_path.name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(str(local_path))
    uri = f"gs://{bucket_name}/{blob_name}"
    print(f"  GCS uploaded: {uri}")
    return uri


def upload_directory(
    local_dir: Path,
    gcs_prefix: str,
    bucket_name: str = DEFAULT_BUCKET,
    suffix: str = ".parquet",
) -> list[str]:
    """Upload all files with given suffix from a directory to GCS."""
    uris = []
    for path in sorted(local_dir.glob(f"*{suffix}")):
        uri = upload_file(path, gcs_prefix, bucket_name)
        uris.append(uri)
    return uris


def list_blobs(
    gcs_prefix: str,
    bucket_name: str = DEFAULT_BUCKET,
) -> list[str]:
    """List all blob names under a GCS prefix."""
    client = get_client()
    bucket = client.bucket(bucket_name)
    return [blob.name for blob in bucket.list_blobs(prefix=gcs_prefix)]
