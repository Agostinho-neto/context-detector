terraform {
  required_version = ">= 1.10, < 2.0"

  backend "gcs" {
    bucket = "context-detector-dev-tfstate"
    prefix = "context-detector/terraform"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.45"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}