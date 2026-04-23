"""Inspect GCS bucket contents for the interior minister data lake."""

from google.cloud import storage

BUCKET = "interior-minister-data-lake-fabled-imagery-488015-p6"

def main():
    client = storage.Client()
    bucket = client.bucket(BUCKET)

    prefixes = ["raw/tabular/", "raw/geographic/", "processed/tabular/", "processed/geographic/", "knowledge_graph/"]

    for prefix in prefixes:
        blobs = list(bucket.list_blobs(prefix=prefix))
        # Filter out folder markers
        files = [b for b in blobs if not b.name.endswith("/")]
        print(f"\n{prefix} ({len(files)} files)")
        for blob in files:
            size_mb = blob.size / (1024 * 1024) if blob.size else 0
            print(f"  {blob.name} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
