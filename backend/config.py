import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./edtech_verifier.db")

    class Config:
        env_file = ".env"

settings = Settings()
