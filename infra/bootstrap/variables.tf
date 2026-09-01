variable "project_id" {
  description = "ID do projeto no Google Cloud"
  type        = string
}

variable "github_repository" {
  description = "Repositório autorizado no formato owner/repository"
  type        = string
}

variable "terraform_state_bucket" {
  description = "Bucket que armazena o estado da infraestrutura"
  type        = string
}