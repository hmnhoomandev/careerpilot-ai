output "api_uri" { value = google_cloud_run_v2_service.api.uri }
output "web_uri" { value = google_cloud_run_v2_service.web.uri }
output "artifact_repository" { value = google_artifact_registry_repository.containers.name }
output "database_connection_name" { value = google_sql_database_instance.main.connection_name }

