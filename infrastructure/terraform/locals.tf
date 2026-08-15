locals {
  name = "careerpilot-${var.environment}"
  labels = {
    application = "careerpilot"
    environment = var.environment
    managed_by  = "terraform"
    residency   = "ch"
  }
}

