from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---- JWT ----
    secret_key_name: str                       # Key Vault secret base name, e.g. "USERS-JWT-KEY"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60
    jwt_audience: str                          # used as the `aud` claim (replaces gcp project_id)

    # ---- Azure resources ----
    key_vault_url: str                         # https://<vault>.vault.azure.net
    service_bus_namespace: str                 # <namespace>.servicebus.windows.net  (FQDN, no scheme)
    service_bus_topic: str                     # e.g. users-events
    service_bus_subscription: str = "users-service"

    # ---- Database ----
    db_creds_secret: str = "USERS-DB-CREDS"    # Key Vault secret name holding the dotenv-style creds blob

    # ---- Cosmos DB (replacement for GCP Datastore) ----
    cosmos_endpoint: str                       # https://<account>.documents.azure.com:443/
    cosmos_database: str = "comparena"         # ≈ old Datastore database "cloud-hw1"

    # Read from env, then fall back to settings.env (for local dev)
    model_config = SettingsConfigDict(
        env_file="settings.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
