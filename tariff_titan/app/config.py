from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # API Keys
    MISTRAL_API_KEY: str
    GEMINI_API_KEY: str
    
    # Endee Vector DB connection
    ENDEE_HOST: str = "http://localhost"
    ENDEE_PORT: int = 8888
    
    # Feedback Logs
    FEEDBACK_LOG_PATH: str = os.path.join(os.path.dirname(__file__), "feedback_log.json")

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

settings = Settings()
