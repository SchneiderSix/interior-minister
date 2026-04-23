output "bucket_name" {
  description = "GCS data lake bucket name"
  value       = google_storage_bucket.data_lake.name
}

output "bucket_url" {
  description = "GCS data lake bucket URL"
  value       = google_storage_bucket.data_lake.url
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.interior_minister.dataset_id
}

output "service_account_email" {
  description = "Pipeline service account email"
  value       = google_service_account.pipeline.email
}
