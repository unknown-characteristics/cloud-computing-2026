from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "assignment-service"
    FIRESTORE_PROJECT_ID: str = "your-gcp-project-id"
    PUBSUB_TOPIC: str = "assignment-events"

    class Config:
        env_file = ".env"


settings = Settings()
