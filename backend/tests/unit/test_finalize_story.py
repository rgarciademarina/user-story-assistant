import pytest
from unittest.mock import Mock, AsyncMock
from src.llm.service import LLMService, ChatMessageHistory
from src.config.llm_config import LLMConfig
from src.llm.models import ProcessState
from langchain_ollama import OllamaLLM
from uuid import uuid4

@pytest.fixture
def mock_ollama_llm():
    mock = Mock(spec=OllamaLLM)
    async def mock_ainvoke(messages):
        prompt = str(messages)
        if "gherkin" in prompt.lower():
            response = """**Historia Finalizada:**
Como usuario quiero iniciar sesión con email y contraseña para acceder de forma segura a mi cuenta

**Criterios de Aceptación (Gherkin):**
Given un usuario registrado en el sistema
  And tiene credenciales válidas
When intenta iniciar sesión con email y contraseña correctos
Then debe obtener acceso a su cuenta
  And debe recibir un token de autenticación
  And debe ser redirigido a su página principal

**Feedback de Mejoras:**
Se han añadido validaciones de seguridad y formato Gherkin"""
        elif "Historia de Usuario:" in prompt:
            response = """**Historia Finalizada:**
Como usuario quiero iniciar sesión con email y contraseña para acceder de forma segura a mi cuenta

**Criterios de Aceptación:**
Given un usuario registrado
When intenta iniciar sesión con credenciales válidas
Then debe obtener acceso a su cuenta

**Feedback de Mejoras:**
Se han añadido validaciones de seguridad"""
        else:
            response = """**Historia Finalizada:**
Historia finalizada de prueba
**Feedback de Mejoras:**
Feedback de prueba"""
        return response
    
    mock.ainvoke = AsyncMock(side_effect=mock_ainvoke)
    mock.model = "test-model"
    mock.base_url = "http://test-url"
    mock.temperature = 0.7
    return mock

@pytest.fixture
def llm_config(mock_ollama_llm):
    return LLMConfig(
        llm=mock_ollama_llm,
        refinement_prompt_template="Refina la historia: {story}",
        corner_case_prompt_template="Identifica casos esquina: {story}",
        testing_strategy_prompt_template="Propón estrategias: {story}"
    )

@pytest.fixture
def llm_service(llm_config):
    service = LLMService(config=llm_config, llm=llm_config.llm)
    service.llm = llm_config.llm
    return service

@pytest.mark.asyncio
async def test_finalize_story_with_components(llm_service):
    """Test finalizar historia con componentes individuales"""
    session_id = llm_service.create_session()

    result = await llm_service.finalize_story(
        session_id=session_id,
        story_input="Como usuario quiero iniciar sesión",
        corner_cases=["Credenciales inválidas"],
        testing_strategy=["Pruebas unitarias"]
    )

    assert "finalized_story" in result
    assert "feedback" in result
    assert isinstance(result["finalized_story"], str)
    assert isinstance(result["feedback"], str)

    # Verificar que la sesión se actualizó
    session = llm_service._get_session(session_id)
    assert session.finalized_story == result["finalized_story"]

@pytest.mark.asyncio
async def test_finalize_story_with_existing_story(llm_service):
    """Test finalizar historia con una historia existente y feedback"""
    session_id = llm_service.create_session()

    result = await llm_service.finalize_story(
        session_id=session_id,
        story_input="""Historia Principal:
Como usuario quiero iniciar sesión

Criterios de Aceptación:
Given un usuario registrado
When intenta iniciar sesión
Then debe obtener acceso""",
        feedback="Añadir validación de contraseña"
    )

    assert "finalized_story" in result
    assert "feedback" in result
    assert isinstance(result["finalized_story"], str)
    assert isinstance(result["feedback"], str)

    # Verificar que la sesión se actualizó
    session = llm_service._get_session(session_id)
    assert session.finalized_story == result["finalized_story"]

@pytest.mark.asyncio
async def test_finalize_story_with_format_preferences(llm_service):
    """Test finalizar historia con preferencias de formato específicas"""
    session_id = llm_service.create_session()

    format_preferences = {
        "acceptance_criteria_format": "gherkin",
        "functional_tests_format": "markdown"
    }

    result = await llm_service.finalize_story(
        session_id=session_id,
        story_input="Como usuario quiero iniciar sesión",
        corner_cases=["Credenciales inválidas"],
        testing_strategy=["Pruebas unitarias"],
        format_preferences=format_preferences
    )

    assert "finalized_story" in result
    assert "feedback" in result
    # Verificar que el formato Gherkin está presente
    assert "Given" in result["finalized_story"]
    assert "When" in result["finalized_story"]
    assert "Then" in result["finalized_story"]

@pytest.mark.asyncio
async def test_finalize_story_error_handling(llm_service):
    """Test el manejo de errores al finalizar una historia"""
    invalid_session_id = uuid4()  # ID de sesión inválido

    with pytest.raises(ValueError, match="Sesión no encontrada"):
        await llm_service.finalize_story(
            session_id=invalid_session_id,
            story_input="Como usuario quiero iniciar sesión",
            corner_cases=["Credenciales inválidas"],
            testing_strategy=["Pruebas unitarias"]
        )
