import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.dependencies import override_llm_service
from tests.mocks.mock_llm import MockLLMService
from src.llm.config import LLMConfig, get_llm_config
from unittest.mock import patch
import asyncio

@pytest.fixture
def llm_config():
    """Fixture que proporciona una configuración de prueba para el LLM"""
    return LLMConfig(
        model_name="llama3.2-vision",
        model_type="ollama",
        ollama_base_url="http://localhost:11434",
        max_length=2048,
        temperature=0.7,
        api_host="0.0.0.0",
        api_port=8000,
        environment="testing",
        log_level="DEBUG",
        debug=True,
        vector_store_path="./data/vector_store"
    )       

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
def mock_llm_service():
    """
    Fixture que proporciona un servicio LLM simulado para pruebas.
    """
    return MockLLMService()

@pytest.fixture
def client(mock_llm_service):
    """
    Fixture que proporciona un cliente de prueba con el servicio LLM simulado.
    """
    override_llm_service(mock_llm_service)
    return TestClient(app)

@pytest.fixture
def anyio_backend():
    """Fixture que proporciona el backend para tests asíncronos"""
    return 'asyncio'