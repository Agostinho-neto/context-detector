output "workload_identity_provider" {
  description = "Provider usado pelo GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "service_account_email" {
  description = "Conta de serviço usada pelo GitHub Actions"
  value       = google_service_account.github_actions.email
}