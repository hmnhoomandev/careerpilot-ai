resource "google_compute_network" "main" {
  name                    = local.name
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "main" {
  name                     = local.name
  region                   = var.region
  network                  = google_compute_network.main.id
  ip_cidr_range            = "10.42.0.0/24"
  private_ip_google_access = true
}

resource "google_compute_global_address" "service_range" {
  name          = "${local.name}-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_services" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.service_range.name]
}

resource "google_artifact_registry_repository" "containers" {
  location               = var.region
  repository_id          = local.name
  description            = "Digest-pinned CareerPilot container images"
  format                 = "DOCKER"
  labels                 = local.labels
  cleanup_policy_dry_run = true
}

resource "google_kms_key_ring" "main" {
  name     = local.name
  location = var.region
}

resource "google_kms_crypto_key" "application" {
  name            = "application-data"
  key_ring        = google_kms_key_ring.main.id
  rotation_period = "7776000s"
  lifecycle { prevent_destroy = true }
}

resource "google_secret_manager_secret" "database" {
  secret_id = "${local.name}-database-url"
  labels    = local.labels
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_service_account" "api" {
  account_id   = "cp-${var.environment}-api"
  display_name = "CareerPilot ${var.environment} API runtime"
}

resource "google_service_account" "web" {
  account_id   = "cp-${var.environment}-web"
  display_name = "CareerPilot ${var.environment} web runtime"
}

resource "google_service_account" "migration" {
  account_id   = "cp-${var.environment}-migration"
  display_name = "CareerPilot ${var.environment} schema migration"
}

resource "google_project_iam_member" "api_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_secret_manager_secret_iam_member" "api_database" {
  secret_id = google_secret_manager_secret.database.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}

resource "google_sql_database_instance" "main" {
  name                = local.name
  region              = var.region
  database_version    = "POSTGRES_17"
  deletion_protection = var.deletion_protection
  depends_on          = [google_service_networking_connection.private_services]

  settings {
    tier              = var.environment == "production" ? "db-custom-2-7680" : "db-custom-1-3840"
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"
    disk_autoresize   = true
    disk_type         = "PD_SSD"
    user_labels       = local.labels
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings { retained_backups = 14 }
    }
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
      ssl_mode        = "ENCRYPTED_ONLY"
    }
    insights_config {
      query_insights_enabled  = true
      record_application_tags = true
      record_client_address   = false
    }
  }
}

resource "google_sql_database" "application" {
  name     = "careerpilot"
  instance = google_sql_database_instance.main.name
}

resource "google_pubsub_topic" "events" {
  name                       = "${local.name}-events"
  labels                     = local.labels
  message_retention_duration = "604800s"
  message_storage_policy {
    allowed_persistence_regions = [var.region]
    enforce_in_transit          = true
  }
}

resource "google_cloud_run_v2_service" "api" {
  name                = "${local.name}-api"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"
  deletion_protection = var.deletion_protection
  labels              = local.labels
  template {
    service_account                  = google_service_account.api.email
    timeout                          = "60s"
    max_instance_request_concurrency = 40
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    vpc_access {
      network_interfaces {
        network    = google_compute_network.main.name
        subnetwork = google_compute_subnetwork.main.name
      }
      egress = "PRIVATE_RANGES_ONLY"
    }
    containers {
      image = var.api_image
      ports { container_port = 8080 }
      resources {
        limits   = { cpu = "1", memory = "1Gi" }
        cpu_idle = true
      }
      env {
        name  = "CAREERPILOT_ENVIRONMENT"
        value = var.environment
      }
      env {
        name = "CAREERPILOT_DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database.secret_id
            version = "latest"
          }
        }
      }
      startup_probe {
        http_get {
          path = "/health/live"
        }
        initial_delay_seconds = 2
        timeout_seconds       = 2
        period_seconds        = 5
        failure_threshold     = 12
      }
      liveness_probe {
        http_get {
          path = "/health/live"
        }
        timeout_seconds   = 2
        period_seconds    = 10
        failure_threshold = 3
      }
    }
  }
}

resource "google_cloud_run_v2_service" "web" {
  name                = "${local.name}-web"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = var.deletion_protection
  labels              = local.labels
  template {
    service_account                  = google_service_account.web.email
    max_instance_request_concurrency = 80
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    containers {
      image = var.web_image
      ports { container_port = 3000 }
      resources {
        limits   = { cpu = "1", memory = "512Mi" }
        cpu_idle = true
      }
    }
  }
}

resource "google_cloud_run_v2_job" "migration" {
  name                = "${local.name}-migration"
  location            = var.region
  deletion_protection = var.deletion_protection
  labels              = local.labels
  template {
    template {
      service_account = google_service_account.migration.email
      max_retries     = 0
      timeout         = "600s"
      containers {
        image   = var.api_image
        command = ["alembic"]
        args    = ["upgrade", "head"]
      }
    }
  }
}
