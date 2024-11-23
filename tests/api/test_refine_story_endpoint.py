import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.dependencies import override_llm_service
from tests.mocks.mock_llm import MockLLMService
from uuid import UUID, uuid4

@pytest.fixture
def mock_llm():
    return MockLLMService()

@pytest.fixture
def client(mock_llm):
    override_llm_service(mock_llm)
    return TestClient(app)

def test_refine_story_endpoint_success(client):
    """Test que el endpoint de refinamiento funciona correctamente"""
    response = client.post(
        "/api/v1/refine_story",
        json={
            "story": "Como usuario quiero iniciar sesión"
        }
    )
    assert response.status_code == 200
    assert "refined_story" in response.json()
    assert "refinement_feedback" in response.json()
    assert isinstance(response.json()["session_id"], str)

def test_refine_story_endpoint_with_feedback(client):
    """Test que el endpoint maneja correctamente el feedback"""
    response = client.post(
        "/api/v1/refine_story",
        json={
            "story": "Como usuario quiero iniciar sesión",
            "feedback": "Especificar método de autenticación"
        }
    )
    assert response.status_code == 200
    assert "refined_story" in response.json()
    assert "refinement_feedback" in response.json()

def test_refine_story_endpoint_with_session(client):
    """Test que el endpoint mantiene el contexto de la sesión"""
    session_id = str(uuid4())
    response = client.post(
        "/api/v1/refine_story",
        json={
            "session_id": session_id,
            "story": "Como usuario quiero iniciar sesión"
        }
    )
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id