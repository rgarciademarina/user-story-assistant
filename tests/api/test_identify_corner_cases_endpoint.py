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

def test_identify_corner_cases_endpoint_success(client):
    """Test que el endpoint de identificación de casos esquina funciona correctamente"""
    response = client.post(
        "/api/v1/identify_corner_cases",
        json={
            "story": "Como usuario registrado quiero iniciar sesión con email y contraseña"
        }
    )
    assert response.status_code == 200
    assert "corner_cases" in response.json()
    assert "corner_cases_feedback" in response.json()
    assert isinstance(response.json()["session_id"], str)
    assert isinstance(response.json()["corner_cases"], list)

def test_identify_corner_cases_endpoint_with_feedback(client):
    """Test que el endpoint maneja correctamente el feedback"""
    response = client.post(
        "/api/v1/identify_corner_cases",
        json={
            "story": "Como usuario registrado quiero iniciar sesión con email y contraseña",
            "feedback": "Considerar casos de seguridad",
            "existing_corner_cases": ["Usuario ingresa credenciales incorrectas"]
        }
    )
    assert response.status_code == 200
    assert "corner_cases" in response.json()
    assert "corner_cases_feedback" in response.json()

def test_identify_corner_cases_endpoint_with_session(client):
    """Test que el endpoint mantiene el contexto de la sesión"""
    session_id = str(uuid4())
    response = client.post(
        "/api/v1/identify_corner_cases",
        json={
            "session_id": session_id,
            "story": "Como usuario registrado quiero iniciar sesión con email y contraseña"
        }
    )
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id