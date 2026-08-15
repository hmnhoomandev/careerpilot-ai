variable "project_id" {
  description = "Dedicated Google Cloud project for this environment."
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid Google Cloud project ID."
  }
}

variable "environment" {
  description = "Isolated deployment environment."
  type        = string
  validation {
    condition     = contains(["test", "staging", "production"], var.environment)
    error_message = "environment must be test, staging, or production."
  }
}

variable "region" {
  description = "Swiss residency region; changing this requires a documented exception."
  type        = string
  default     = "europe-west6"
  validation {
    condition     = var.region == "europe-west6"
    error_message = "Phase 17 permits only the Zurich region europe-west6."
  }
}

variable "api_image" {
  description = "Immutable API image reference including @sha256 digest."
  type        = string
  validation {
    condition     = can(regex("@sha256:[0-9a-f]{64}$", var.api_image))
    error_message = "api_image must be immutable and digest pinned."
  }
}

variable "web_image" {
  description = "Immutable web image reference including @sha256 digest."
  type        = string
  validation {
    condition     = can(regex("@sha256:[0-9a-f]{64}$", var.web_image))
    error_message = "web_image must be immutable and digest pinned."
  }
}

variable "deletion_protection" {
  description = "Must remain enabled in production."
  type        = bool
  default     = true
  validation {
    condition     = var.environment != "production" || var.deletion_protection
    error_message = "Production deletion protection cannot be disabled."
  }
}

