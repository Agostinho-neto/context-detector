output "artifact_registry_repository" {
  description = "Endereço do repositório Docker"
  value = format(
    "%s-docker.pkg.dev/%s/%s",
    var.region,
    var.project_id,
    var.repository_id,
  )
}

output "cloud_run_url" {
  description = "URL pública do Context Detector"
  value       = google_cloud_run_v2_service.context_detector.uri
}

output "cloud_run_service_account" {
  description = "Identidade utilizada pelo Cloud Run"
  value       = google_service_account.cloud_run.email
}