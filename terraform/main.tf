terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.24.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  bucket_name = var.bucket_name != "" ? var.bucket_name : "interior-minister-data-lake-${var.project_id}"
}

# --- GCS Data Lake Bucket ---

resource "google_storage_bucket" "data_lake" {
  name          = local.bucket_name
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

# Folder markers for organizational structure
resource "google_storage_bucket_object" "folder_raw_tabular" {
  name    = "raw/tabular/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

resource "google_storage_bucket_object" "folder_raw_geographic" {
  name    = "raw/geographic/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

resource "google_storage_bucket_object" "folder_processed_tabular" {
  name    = "processed/tabular/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

resource "google_storage_bucket_object" "folder_processed_geographic" {
  name    = "processed/geographic/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

resource "google_storage_bucket_object" "folder_knowledge_graph" {
  name    = "knowledge_graph/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

# --- BigQuery Dataset ---

resource "google_bigquery_dataset" "interior_minister" {
  dataset_id = "interior_minister"
  location   = var.bq_location

  description = "Uruguay Interior Ministry crime and justice data warehouse"

  delete_contents_on_destroy = true
}

# --- Service Account ---

resource "google_service_account" "pipeline" {
  account_id   = "interior-minister-pipeline"
  display_name = "Interior Minister Pipeline Service Account"
  description  = "Service account for Interior Ministry data pipeline"
}

resource "google_project_iam_member" "pipeline_gcs" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_project_iam_member" "pipeline_bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_project_iam_member" "pipeline_bq_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}
