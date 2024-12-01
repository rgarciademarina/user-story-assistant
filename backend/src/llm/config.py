from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv('.env')

class LLMConfig(BaseModel):
    """Configuración para el servicio LLM"""
    MODEL_NAME: str = Field(default_factory=lambda: os.getenv('MODEL_NAME', 'llama3.2-vision'))
    MODEL_TYPE: str = Field(default_factory=lambda: os.getenv('MODEL_TYPE', 'ollama'))
    OLLAMA_BASE_URL: str = Field(default_factory=lambda: os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))
    MAX_LENGTH: int = Field(default_factory=lambda: int(os.getenv('MAX_LENGTH', '2048')))
    TEMPERATURE: float = Field(default_factory=lambda: float(os.getenv('TEMPERATURE', '0.7')))
    API_HOST: str = Field(default_factory=lambda: os.getenv('API_HOST', '0.0.0.0'))
    API_PORT: int = Field(default_factory=lambda: int(os.getenv('API_PORT', '8000')))
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    LOG_LEVEL: str = Field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    DEBUG: bool = Field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    VECTOR_STORE_PATH: str = Field(default_factory=lambda: os.getenv('VECTOR_STORE_PATH', './data/vector_store'))
    MAX_LENGTH: int = Field(default_factory=lambda: int(os.getenv('MAX_LENGTH', '2048')))
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
