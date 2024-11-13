from pydantic_settings import BaseSettings
from typing import Optional

class LLMConfig(BaseSettings):
    """Configuración para el servicio LLM"""
    MODEL_NAME: str
    MODEL_TYPE: str
    OLLAMA_BASE_URL: str
    MAX_LENGTH: int
    TEMPERATURE: float

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_llm_config() -> LLMConfig:
    """Retorna una instancia de la configuración"""
    config = LLMConfig()
    print(config.dict())
    return config
