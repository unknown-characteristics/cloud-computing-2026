from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SERVICE_NAME: str = "assignments-service"
    
    # ---- Azure Cosmos DB (replaces GCP Datastore) ----
    cosmos_endpoint: str
    cosmos_database: str = "comparena-cosmos"

    # ---- Azure Service Bus (replaces GCP Pub/Sub) ----
    service_bus_namespace: str
    service_bus_topic: str = "assignments-events"
    service_bus_subscription: str = "assignments-sub"

    model_config = SettingsConfigDict(
        env_file="settings.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()