from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "submissions-service"
    PROJECT_ID: str = "cloudcomputing-491711"
    PUBSUB_TOPIC: str = "submissions-events"
    GCS_BUCKET_NAME: str = "cc-hw1-submissions-bucket"

    class Config:
        env_file = ".env"

settings = Settings()