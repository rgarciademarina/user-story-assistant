import pytest
from httpx import AsyncClient
from src.main import app
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

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_refine_story_endpoint(llm_service, monkeypatch):
    async with AsyncClient(app=app, base_url="http://test") as client:
        sample_story = {
            'story': 'Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal'
        }
        response = await client.post("/refine_story", json=sample_story)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"
        response_json = response.json()
        assert "refined_story" in response_json, "Falta la clave 'refined_story' en la respuesta"
        refined_story = response_json["refined_story"]
        assert isinstance(refined_story, str), "El valor de 'refined_story' debe ser una cadena"
        assert len(refined_story.strip()) > 0, "El valor de 'refined_story' no debe estar vacío"
