from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

# Verificar la ubicación del archivo .env
env_path = os.path.abspath('.env')
print(f"Cargando archivo .env desde: {env_path}")
load_dotenv('.env')

class LLMConfig(BaseSettings):
    """Configuración para el servicio LLM"""
    MODEL_NAME: str
    MODEL_TYPE: str
    OLLAMA_BASE_URL: str
    MAX_LENGTH: int
    TEMPERATURE: float
    API_HOST: str
    API_PORT: int
    ENVIRONMENT: str
    LOG_LEVEL: str
    DEBUG: bool
    VECTOR_STORE_PATH: str

    # Uso de ConfigDict para Pydantic 2
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

def get_llm_config() -> LLMConfig:
    """Retorna una instancia de la configuración"""
    try:
        config = LLMConfig()
        print("### Valores de configuración cargados ###")
        for key, value in config.model_dump().items():
            print(f"{key}: {value} (tipo: {type(value)})")
        print("#########################################")
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        raise
    return config
