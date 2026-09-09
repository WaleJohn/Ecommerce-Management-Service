terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0, < 6.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.12"
    }
  }
}

provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
  resource_providers_to_register = [
    "Microsoft.App",
    "Microsoft.ContainerRegistry",
    "Microsoft.ManagedIdentity",
    "Microsoft.OperationalInsights",
  ]
}

resource "random_string" "suffix" {
  length  = 6
  lower   = true
  numeric = true
  special = false
  upper   = false
}

locals {
  name_prefix     = lower(replace(var.project_name, "_", "-"))
  acr_name_prefix = substr("${lower(replace(var.project_name, "/[^a-zA-Z0-9]/", ""))}${lower(replace(var.environment, "/[^a-zA-Z0-9]/", ""))}", 0, 41)
  common_tags = merge(
    {
      application = var.project_name
      managed_by  = "terraform"
    },
    var.tags
  )

  image_name = "${var.container_image_repository}:${var.image_tag}"
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.name_prefix}-${var.environment}"
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${local.name_prefix}-${var.environment}-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days
  tags                = local.common_tags
}

resource "azurerm_container_registry" "main" {
  name                = "acr${local.acr_name_prefix}${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.acr_sku
  admin_enabled       = false
  tags                = local.common_tags
}

resource "azurerm_user_assigned_identity" "container_app" {
  name                = "id-${local.name_prefix}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_role_assignment" "container_app_acr_pull" {
  scope                            = azurerm_container_registry.main.id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_user_assigned_identity.container_app.principal_id
  skip_service_principal_aad_check = true
}

resource "time_sleep" "wait_for_acr_pull_assignment" {
  create_duration = "60s"

  depends_on = [
    azurerm_role_assignment.container_app_acr_pull
  ]
}

resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${local.name_prefix}-${var.environment}-${random_string.suffix.result}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  logs_destination           = "log-analytics"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags                       = local.common_tags
}

resource "null_resource" "acr_build" {
  triggers = {
    acr_login_server = azurerm_container_registry.main.login_server
    image_name       = local.image_name
    dockerfile_hash  = filesha256("${path.module}/../Dockerfile")
    app_hash         = sha256(join("", [for file in fileset("${path.module}/../app", "**/*.py") : filesha256("${path.module}/../app/${file}")]))
    requirements     = filesha256("${path.module}/../requirements.txt")
  }

  provisioner "local-exec" {
    command     = <<-EOT
      az acr login --name ${azurerm_container_registry.main.name}
      if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

      docker build --tag ${azurerm_container_registry.main.login_server}/${local.image_name} .
      if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

      docker push ${azurerm_container_registry.main.login_server}/${local.image_name}
      if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    EOT
    working_dir = abspath("${path.module}/..")
    interpreter = var.local_exec_interpreter
  }

  depends_on = [
    azurerm_container_registry.main
  ]
}

resource "azurerm_container_app" "api" {
  name                         = "ca-${local.name_prefix}-${var.environment}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.common_tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.container_app.id]
  }

  registry {
    server   = azurerm_container_registry.main.login_server
    identity = azurerm_user_assigned_identity.container_app.id
  }

  ingress {
    external_enabled = true
    target_port      = var.container_port
    transport        = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = "api"
      image  = "${azurerm_container_registry.main.login_server}/${local.image_name}"
      cpu    = var.cpu
      memory = var.memory

      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }
    }
  }

  depends_on = [
    time_sleep.wait_for_acr_pull_assignment,
    null_resource.acr_build
  ]
}
