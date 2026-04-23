variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "US"
}

variable "bq_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

variable "bucket_name" {
  description = "Override default bucket name (leave empty for auto-generated)"
  type        = string
  default     = ""
}
