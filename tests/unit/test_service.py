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
        _env_file=None  # Evita que busque el archivo .env
    )

@pytest.fixture
def llm_service(llm_config):
    """Fixture que proporciona una instancia del servicio LLM"""
    return LLMService(config=llm_config)

@pytest.mark.asyncio  # Marca el test como asíncrono
async def test_analyze_user_story(llm_service):
    user_story = """
    Como usuario quiero poder iniciar sesión 
    para acceder a mi cuenta personal
    """
    result = await llm_service.analyze_user_story(user_story)
    
    assert isinstance(result, dict)
    assert "improvements" in result
    assert "edge_cases" in result
    assert "testing_strategies" in result

@pytest.mark.asyncio
async def test_analyze_user_story_response_structure(llm_service):
    """Test que verifica la estructura detallada de la respuesta"""
    user_story = """
    Como usuario quiero poder iniciar sesión 
    para acceder a mi cuenta personal
    """
    result = await llm_service.analyze_user_story(user_story)
    
    # Verificar estructura básica
    assert isinstance(result, dict)
    assert "improvements" in result
    assert "edge_cases" in result
    assert "testing_strategies" in result
    
    # Verificar que cada campo es una lista
    assert isinstance(result["improvements"], list)
    assert isinstance(result["edge_cases"], list)
    assert isinstance(result["testing_strategies"], list)
    
    # Verificar que las listas no están vacías
    assert len(result["improvements"]) > 0
    assert len(result["edge_cases"]) > 0
    assert len(result["testing_strategies"]) > 0
