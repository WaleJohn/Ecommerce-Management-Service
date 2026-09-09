variable "project_name" {
  description = "Base name used for Azure resources."
  type        = string
  default     = "ecommerce-api"

  validation {
    condition     = can(regex("^[A-Za-z0-9][A-Za-z0-9_-]{1,38}[A-Za-z0-9]$", var.project_name))
    error_message = "project_name must be 3-40 characters, start and end with a letter or number, and contain only letters, numbers, hyphens, or underscores."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"

  validation {
    condition     = can(regex("^[A-Za-z0-9][A-Za-z0-9-]{0,14}[A-Za-z0-9]$", var.environment))
    error_message = "environment must be 2-16 characters, start and end with a letter or number, and contain only letters, numbers, or hyphens."
  }
}

variable "location" {
  description = "Azure region for all resources."
  type        = string
  default     = "eastus"
}

variable "subscription_id" {
  description = "Azure subscription ID. Leave null to use ARM_SUBSCRIPTION_ID or the Azure CLI default subscription."
  type        = string
  default     = null
}

variable "acr_sku" {
  description = "Azure Container Registry SKU."
  type        = string
  default     = "Basic"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "acr_sku must be Basic, Standard, or Premium."
  }
}

variable "container_image_repository" {
  description = "Repository name inside Azure Container Registry."
  type        = string
  default     = "ecommerce-api"

  validation {
    condition     = can(regex("^[a-z0-9]+([._/-][a-z0-9]+)*$", var.container_image_repository))
    error_message = "container_image_repository must be a valid lowercase container repository name."
  }
}

variable "image_tag" {
  description = "Container image tag to build and deploy."
  type        = string
  default     = "latest"
}

variable "container_port" {
  description = "Port exposed by the FastAPI container."
  type        = number
  default     = 8000

  validation {
    condition     = var.container_port > 0 && var.container_port <= 65535
    error_message = "container_port must be between 1 and 65535."
  }
}

variable "cpu" {
  description = "CPU allocation for the Container App."
  type        = number
  default     = 0.5

  validation {
    condition     = contains([0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2], var.cpu)
    error_message = "cpu must be one of the CPU values supported by Azure Container Apps, such as 0.25, 0.5, 1, or 2."
  }
}

variable "memory" {
  description = "Memory allocation for the Container App."
  type        = string
  default     = "1Gi"

  validation {
    condition     = can(regex("^[0-9]+(\\.[0-9]+)?Gi$", var.memory))
    error_message = "memory must use Azure Container Apps Gi notation, such as 0.5Gi, 1Gi, or 2Gi."
  }
}

variable "min_replicas" {
  description = "Minimum number of Container App replicas."
  type        = number
  default     = 1
}

variable "max_replicas" {
  description = "Maximum number of Container App replicas."
  type        = number
  default     = 3

  validation {
    condition     = var.max_replicas >= var.min_replicas
    error_message = "max_replicas must be greater than or equal to min_replicas."
  }
}

variable "log_retention_days" {
  description = "Log Analytics retention period in days."
  type        = number
  default     = 30
}

variable "local_exec_interpreter" {
  description = "Interpreter for Terraform local-exec commands. Default works in Windows PowerShell."
  type        = list(string)
  default     = ["PowerShell", "-Command"]
}

variable "tags" {
  description = "Additional tags applied to Azure resources."
  type        = map(string)
  default     = {}
}
