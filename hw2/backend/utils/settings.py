from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_KEY: str
    DB_URL: str
    TOKEN_EXPIRE_MINUTES: int
    CONTREST_URL: str
    DEFAULT_ADMIN_PASSWORD: str
    GEMINI_KEY: str
    NINJAS_KEY: str
    UNSPLASH_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
