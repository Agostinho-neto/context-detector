variable "project_id" {
  description = "ID do projeto no Google Cloud"
  type        = string
}

variable "region" {
  description = "Região dos recursos no Google Cloud"
  type        = string
  default     = "us-central1"
}

variable "repository_id" {
  description = "Nome do repositório Docker no Artifact Registry"
  type        = string
  default     = "context-detector"
}

variable "service_name" {
  description = "Nome do serviço no Cloud Run"
  type        = string
  default     = "context-detector"
}

variable "image_name" {
  description = "Nome da imagem no Artifact Registry"
  type        = string
  default     = "context-detector"
}

variable "image_tag" {
  description = "Versão da imagem que será implantada"
  type        = string
  default     = "v1.0.0"
}