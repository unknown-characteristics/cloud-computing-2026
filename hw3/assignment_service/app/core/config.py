from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str
    PROJECT_ID: str
    PUBSUB_TOPIC: str

    class Config:
        env_file = "settings.env"


settings = Settings()
