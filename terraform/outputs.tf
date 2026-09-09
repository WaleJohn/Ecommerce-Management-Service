output "resource_group_name" {
  description = "Azure resource group name."
  value       = azurerm_resource_group.main.name
}

output "container_registry_name" {
  description = "Azure Container Registry name."
  value       = azurerm_container_registry.main.name
}

output "container_registry_login_server" {
  description = "Azure Container Registry login server."
  value       = azurerm_container_registry.main.login_server
}

output "container_app_name" {
  description = "Azure Container App name."
  value       = azurerm_container_app.api.name
}

output "container_app_fqdn" {
  description = "Public FQDN for the Container App."
  value       = azurerm_container_app.api.ingress[0].fqdn
}

output "api_base_url" {
  description = "Public HTTPS base URL for the API."
  value       = "https://${azurerm_container_app.api.ingress[0].fqdn}"
}

output "api_docs_url" {
  description = "FastAPI Swagger UI URL."
  value       = "https://${azurerm_container_app.api.ingress[0].fqdn}/docs"
}
