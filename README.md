# Ecommerce Management Microservice

A FastAPI microservice for user management, order management, and payment tracking in an ecommerce app.

## Features

- User creation, listing, retrieval, update, and deletion
- Order creation, listing, retrieval, status update, and deletion
- Payment creation, listing, retrieval, and status update
- Payment capture automatically marks the related order as paid
- Docker and Docker Compose support

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.

Interactive docs are available at `http://localhost:8000/docs`.

## Run With Docker

```bash
docker compose up --build
```

If your Docker installation exposes Compose as the standalone command:

```bash
docker-compose up --build
```

## Deploy To Azure

Terraform scripts are available in `terraform/` to deploy the Dockerized API to Azure Container Apps.

The deployment creates a resource group, Azure Container Registry, Log Analytics workspace, managed identity, Container Apps environment, and public Container App. Terraform uses `az acr build`, so Azure builds the image from this repository and local Docker does not need to be running.

Prerequisites:

- Terraform `>= 1.6`
- Azure CLI
- An Azure account with permission to create resource groups, role assignments, ACR, Log Analytics, managed identities, and Container Apps

Deploy from the project root:

```powershell
az login
az account set --subscription "<subscription-id-or-name>"
$env:ARM_SUBSCRIPTION_ID = "<subscription-id>"

cd terraform
terraform init
terraform plan
terraform apply
```

When `terraform apply` completes, Terraform prints:

- `api_base_url`
- `api_docs_url`

Open `api_docs_url` to use the FastAPI Swagger UI.

To customize the Azure region, environment name, replica count, CPU, memory, or image tag:

```powershell
cd terraform
Copy-Item terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`, then run `terraform apply` again.

To tear down the Azure resources:

```powershell
cd terraform
terraform destroy
```

See `terraform/README.md` for the full Terraform variable reference.

## Test

```bash
pytest
```

## API Overview

- `GET /health`
- `POST /users`
- `GET /users`
- `GET /users/{user_id}`
- `PATCH /users/{user_id}`
- `DELETE /users/{user_id}`
- `POST /orders`
- `GET /orders`
- `GET /orders/{order_id}`
- `PATCH /orders/{order_id}`
- `DELETE /orders/{order_id}`
- `POST /payments`
- `GET /payments`
- `GET /payments/{payment_id}`
- `PATCH /payments/{payment_id}`

This starter service uses an in-memory store so it is easy to run and test. For production use, replace `app/repository.py` with a database-backed repository.
