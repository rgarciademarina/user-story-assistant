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
        _env_file=None  # Evita que busque el archivo .env en los tests
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
    
    # Verificar que el resultado es un diccionario
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    
    # Verificar que contiene las claves esperadas
    for key in ["improvements", "edge_cases", "testing_strategies"]:
        assert key in result, f"Falta la clave '{key}' en el resultado"
        assert isinstance(result[key], str), f"El valor de '{key}' debe ser una cadena"
        assert len(result[key].strip()) > 0, f"El valor de '{key}' no debe estar vacío"
