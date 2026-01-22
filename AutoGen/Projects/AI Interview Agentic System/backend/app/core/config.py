from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI
    OPENAI_API_KEY: str

    # Database
    DATABASE_URL: str

    # FAISS
    FAISS_INDEX_PATH: str = "./faiss_index"

    # Interview settings
    INTERVIEW_DURATION_MINUTES: int = 35  # 30-45 min range
    MIN_QUESTIONS: int = 5
    MAX_QUESTIONS: int = 10

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    class Config:
        env_file = "../.env"
        case_sensitive = True


settings = Settings()
