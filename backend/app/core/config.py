from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    app_name: str = "OpsPilot"
    app_version: str = "0.2.0"
    environment: str = "development"
    debug: bool = True
    
    llm_provider: str = "ollama"
    
    openai_api_key: str | None = None
    openai_model: str | None = None
    
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"

    model_config = SettingsConfigDict(
        env_file = ENV_FILE,
        env_file_encoding = "utf-8",
        extra="ignore",
    )
    
settings = Settings()