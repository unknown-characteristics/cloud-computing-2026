# Servicii utilizate

App Engine

Cloud SQL

Datastore

Cloud Storage

Cloud Run

Cloud Pub/Sub

Cloud Tasks

Cloud Scheduler

Secret Manager




az containerapp create \
  --name user-service \
  --resource-group CloudComputing \
  --registry-username "$ACR_USER" \
  --registry-password "$ACR_PASS" \
  --environment comparena-env \
  --image comparenaacr-f5f8cchvgaageffq.azurecr.io/user-service:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server comparenaacr-f5f8cchvgaageffq.azurecr.io \
  --system-assigned \
  --min-replicas 1 \
  --max-replicas 3 \
  --env-vars \
    KEY_VAULT_URL=https://comparena-kv.vault.azure.net \
    SERVICE_BUS_NAMESPACE=comparena.servicebus.windows.net \
    SERVICE_BUS_TOPIC=users-events \
    SERVICE_BUS_SUBSCRIPTION=users-service \
    SECRET_KEY_NAME=USERS-JWT-KEY \
    JWT_AUDIENCE=comparena-users \
    DB_CREDS_SECRET=USERS-DB-CREDS \
    COSMOS_ENDPOINT=https://comparena-cosmos.documents.azure.com:443/ \
    COSMOS_DATABASE=comparena