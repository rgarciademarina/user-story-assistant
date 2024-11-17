import pytest
from src.llm.service import LLMService
from src.llm.config import LLMConfig

@pytest.fixture
def llm_config():
    """Fixture que proporciona una configuración de prueba para el LLM"""
    return LLMConfig(
        MODEL_NAME="llama3.2-vision",
        MODEL_TYPE="ollama",
        OLLAMA_BASE_URL="http://localhost:11434",
        MAX_LENGTH=2048,
        TEMPERATURE=0.7,
        API_HOST="0.0.0.0",
        API_PORT=8000,
        ENVIRONMENT="testing",
        LOG_LEVEL="DEBUG",
        DEBUG=True,
        VECTOR_STORE_PATH="./data/vector_store"
    )

@pytest.fixture
def llm_service(llm_config):
    """Fixture que proporciona una instancia del servicio LLM"""
    return LLMService(config=llm_config)