# Servicii utilizate

Azure App Services (for gateway-appengine, which also serves the compiled frontend in a dist/ folder)

Azure Container Apps (for the 3 microservices)

Azure Container Apps Environments (for the 3 microservices)

Azure Function App (for outbox-flusher)

Azure Service Bus (for communication between microservices)

Azure Cosmos DB (for storing assignments, submissions, ratings)

Azure Database for MySQL flexible servers (for storing user accounts)

Azure Key Vault (for storing JWT keys and DB credentials)

Azure Blob Storage (for storing the actual files in the submissions)

Azure Container Registries (for deploying docker images for the container apps)

Azure Application Insights (for access to outbox-flusher's log stream, for debugging)
