locals {
  required_apis = toset([
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com",
  ])

  image_url = format(
    "%s-docker.pkg.dev/%s/%s/%s:%s",
    var.region,
    var.project_id,
    var.repository_id,
    var.image_name,
    var.image_tag,
  )
}

resource "google_project_service" "required" {
  for_each = local.required_apis

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "context_detector" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_id
  description   = "Imagens Docker do Context Detector"
  format        = "DOCKER"

  depends_on = [
    google_project_service.required,
  ]
}

resource "google_service_account" "cloud_run" {
  project      = var.project_id
  account_id   = "context-detector-run"
  display_name = "Context Detector Cloud Run"
  description  = "Identidade utilizada pela aplicação Context Detector"

  depends_on = [
    google_project_service.required,
  ]
}

resource "google_cloud_run_v2_service" "context_detector" {
  project             = var.project_id
  name                = var.service_name
  location            = var.region
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"

  scaling {
    max_instance_count = 1
  }

  template {
    service_account                  = google_service_account.cloud_run.email
    max_instance_request_concurrency = 20
    timeout                          = "900s"

    containers {
      image = local.image_url

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }

        cpu_idle = true
      }
    }
  }

  depends_on = [
    google_project_service.required,
    google_artifact_registry_repository.context_detector,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = var.project_id
  location = google_cloud_run_v2_service.context_detector.location
  name     = google_cloud_run_v2_service.context_detector.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}