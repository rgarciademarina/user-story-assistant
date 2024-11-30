import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from fastapi import HTTPException
from src.api.routes.finalize_story import finalize_story, FinalizeStoryRequest, FinalizeStoryResponse
from src.llm.service import LLMService
from src.dependencies import get_llm_service

@pytest.mark.asyncio
async def test_finalize_story_successful():
    """Test successful finalization of a story."""
    # Prepare mock request
    mock_request = FinalizeStoryRequest(
        session_id=str(uuid4()),
        refined_story="Test user story",
        corner_cases=["Test corner case"],
        testing_strategy=["Test strategy"],
        feedback=""
    )

    # Create a mock LLM service
    mock_llm_service = AsyncMock(spec=LLMService)
    mock_llm_service.finalize_story.return_value = {
        "finalized_story": """Como usuario registrado, quiero iniciar sesión.    
    
#### Criterios de Aceptación Funcionales
#### Criterio 1 - Inicio de Sesión Correcto
**Dado** que soy un usuario registrado
**Cuando** ingreso credenciales correctas
**Entonces** accedo a mi cuenta

#### Tests Funcionales
#### Test 1 - Inicio de Sesión Básico
**Dado** que soy un usuario registrado
**Cuando** ingreso credenciales válidas
**Entonces** accedo a mi cuenta
""",
        "feedback": ""
    }

    # Patch the get_llm_service dependency to return our mock
    def mock_get_llm_service():
        return mock_llm_service

    with patch('src.api.routes.finalize_story.get_llm_service', side_effect=mock_get_llm_service):
        response = await finalize_story(mock_request, llm_service=mock_llm_service)

    # Assertions
    assert isinstance(response, FinalizeStoryResponse)
    assert response.finalized_story is not None
    assert "#### Criterios de Aceptación Funcionales" in response.finalized_story
    assert "#### Tests Funcionales" in response.finalized_story

@pytest.mark.asyncio
async def test_finalize_story_with_existing_session_id():
    """Test finalization with an existing session ID."""
    existing_session_id = str(uuid4())
    mock_request = FinalizeStoryRequest(
        session_id=existing_session_id,
        refined_story="Test user story",
        corner_cases=["Test corner case"],
        testing_strategy=["Test strategy"],
        feedback=""
    )

    mock_llm_service = AsyncMock(spec=LLMService)
    mock_llm_service.finalize_story.return_value = {
        "finalized_story": "Finalized story content",
        "feedback": ""
    }

    # Patch the get_llm_service dependency to return our mock
    def mock_get_llm_service():
        return mock_llm_service

    with patch('src.api.routes.finalize_story.get_llm_service', side_effect=mock_get_llm_service):
        response = await finalize_story(mock_request, llm_service=mock_llm_service)

    assert isinstance(response.session_id, UUID)
    assert str(response.session_id) == existing_session_id

@pytest.mark.asyncio
async def test_finalize_story_without_session_id():
    """Test finalization without a session ID."""
    mock_request = FinalizeStoryRequest(
        session_id=None,
        refined_story="Test user story",
        corner_cases=["Test corner case"],
        testing_strategy=["Test strategy"],
        feedback=""
    )

    mock_llm_service = AsyncMock(spec=LLMService)
    mock_llm_service.finalize_story.return_value = {
        "finalized_story": "Finalized story content",
        "feedback": ""
    }

    # Patch the get_llm_service dependency to return our mock
    def mock_get_llm_service():
        return mock_llm_service

    with patch('src.api.routes.finalize_story.get_llm_service', side_effect=mock_get_llm_service):
        response = await finalize_story(mock_request, llm_service=mock_llm_service)

    assert isinstance(response.session_id, UUID)
    assert response.session_id is not None

@pytest.mark.asyncio
async def test_finalize_story_no_tests_section():
    """Test handling of a response without a tests section."""
    mock_request = FinalizeStoryRequest(
        session_id=str(uuid4()),
        refined_story="Test user story",
        corner_cases=["Test corner case"],
        testing_strategy=["Test strategy"],
        feedback=""
    )

    mock_llm_service = AsyncMock(spec=LLMService)
    mock_llm_service.finalize_story.return_value = {
        "finalized_story": "Story without tests section",
        "feedback": ""
    }

    # Patch the get_llm_service dependency to return our mock
    def mock_get_llm_service():
        return mock_llm_service

    with patch('src.api.routes.finalize_story.get_llm_service', side_effect=mock_get_llm_service):
        response = await finalize_story(mock_request, llm_service=mock_llm_service)

    assert response.finalized_story == "Story without tests section"
