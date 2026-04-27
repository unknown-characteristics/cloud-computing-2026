from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "submissions-service"

    service_bus_namespace: str                 # <namespace>.servicebus.windows.net  (FQDN, no scheme)
    service_bus_topic: str = "submissions-events"
    service_bus_subscription: str = "submissions-sub"

    # ---- Cosmos DB (replacement for GCP Datastore) ----
    cosmos_endpoint: str                       # https://<account>.documents.azure.com:443/
    cosmos_database: str = "comparena"         # ≈ old Datastore database "cloud-hw1"

    model_config = SettingsConfigDict(
        env_file="settings.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()