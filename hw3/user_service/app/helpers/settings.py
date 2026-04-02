from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # JWT Security
    secret_key_name: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cloud_project_id: str

    # Tell Pydantic to read from the .env file
    model_config = SettingsConfigDict(env_file="settings.env", env_file_encoding="utf-8")

# We instantiate it here so we can just import `settings` anywhere in the app
settings = Settings()