from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    db_user: str
    db_passwd: str
    db_connection_ip: str
    db_name: str
    
    # JWT Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Google Cloud & Vertex AI
    cloud_project_name: str
    cloud_project_location: str
    generative_model: str

    # Tell Pydantic to read from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# We instantiate it here so we can just import `settings` anywhere in the app
settings = Settings()