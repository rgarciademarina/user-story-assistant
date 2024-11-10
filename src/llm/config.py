from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMConfig(BaseSettings):
    """Configuración para el servicio LLM"""
    MODEL_NAME: str
    MODEL_TYPE: str
    OLLAMA_BASE_URL: str
    MAX_LENGTH: int
    TEMPERATURE: float

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # Ignora variables adicionales en .env
    )

def get_llm_config() -> LLMConfig:
    """Retorna una instancia cacheada de la configuración"""
    return LLMConfig()
