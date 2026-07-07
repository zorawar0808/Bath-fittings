import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/hardware_store_ai"
    SECRET_KEY: str = "4eb887f58dbe4e0474e6f9db162e249492ea351b6e4e5ee60fb7f8ab7f8a7e28"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    GEMINI_API_KEY: Optional[str] = None
    PROJECT_NAME: str = "Hardware Store PWA API"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
