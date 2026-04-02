from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "submission-service"
    FIRESTORE_PROJECT_ID: str = "cloudcomputing-491711"
    PUBSUB_TOPIC: str = "submission-events"

    class Config:
        env_file = ".env"

settings = Settings()