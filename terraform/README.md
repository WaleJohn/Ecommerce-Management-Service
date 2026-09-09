# Azure Terraform Deployment

This Terraform configuration deploys the FastAPI ecommerce microservice to Azure Container Apps.

It creates:

- Resource group
- Log Analytics workspace
- Azure Container Registry
- User-assigned managed identity
- `AcrPull` role assignment for the Container App
- Azure Container Apps environment
- Azure Container App with public HTTPS ingress

Terraform also runs `az acr build` to build the local Dockerfile remotely in Azure Container Registry, so Docker does not need to be running locally.

## Prerequisites

- Terraform `>= 1.6`
- Azure CLI
- An authenticated Azure CLI session:

```powershell
az login
az account set --subscription "<subscription-id-or-name>"
```

AzureRM 4+ requires a subscription ID during `plan` and `apply`. Use one of these options:

```powershell
$env:ARM_SUBSCRIPTION_ID = "<subscription-id>"
```

Or set `subscription_id` in `terraform.tfvars`.

Your Azure account needs permissions to create resource groups, managed identities, role assignments, ACR, Log Analytics, and Container Apps.

## Deploy

From this directory:

```powershell
cd terraform
terraform init
terraform plan
terraform apply
```

After apply completes, Terraform prints `api_base_url` and `api_docs_url`.

## Customize

Copy the example variables file and edit values as needed:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```

Common values:

- `location`: Azure region, such as `eastus`, `centralus`, or `westus2`
- `environment`: environment suffix, such as `dev`, `stage`, or `prod`
- `min_replicas` / `max_replicas`: autoscaling range
- `cpu` / `memory`: container resource allocation
- `image_tag`: image tag built and deployed to ACR

For non-Windows shells, set this in `terraform.tfvars`:

```hcl
local_exec_interpreter = ["/bin/sh", "-c"]
```

## Redeploy App Changes

When files under `app/`, `Dockerfile`, or `requirements.txt` change, Terraform reruns `az acr build` and updates the Container App image reference.

```powershell
terraform apply
```

## Destroy

```powershell
terraform destroy
```
