from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv('.env')

class LLMConfig(BaseModel):
    """Configuración para el servicio LLM"""
    MODEL_NAME: str = Field(default="llama3.2-vision")
    MODEL_TYPE: str = Field(default="ollama")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    MAX_LENGTH: int = Field(default=2048)
    TEMPERATURE: float = Field(default=0.7)
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    DEBUG: bool = Field(default=False)
    VECTOR_STORE_PATH: str = Field(default="./data/vector_store")
    model_config = {
        "populate_by_name": True,
        "alias_generator": lambda x: x.lower()
    }

def get_llm_config() -> LLMConfig:
    """Obtiene la configuración del LLM"""
    try:
        return LLMConfig()
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        raise
