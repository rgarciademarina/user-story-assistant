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

def test_propose_testing_strategy_endpoint_success(client):
    """Test que el endpoint de propuesta de estrategias funciona correctamente"""
    response = client.post(
        "/api/v1/propose_testing_strategy",
        json={
            "story": "Como usuario registrado quiero iniciar sesión con email y contraseña",
            "corner_cases": ["Usuario ingresa credenciales incorrectas"]
        }
    )
    assert response.status_code == 200
    assert "testing_strategies" in response.json()
    assert "testing_feedback" in response.json()
    assert isinstance(response.json()["session_id"], str)
    assert isinstance(response.json()["testing_strategies"], list)

def test_propose_testing_strategy_endpoint_with_feedback(client):
    """Test que el endpoint maneja correctamente el feedback"""
    response = client.post(
        "/api/v1/propose_testing_strategy",
        json={
            "story": "Como usuario registrado quiero iniciar sesión con email y contraseña",
            "corner_cases": ["Usuario ingresa credenciales incorrectas"],
            "feedback": "Incluir pruebas de rendimiento",
            "existing_testing_strategies": ["Test de validación de credenciales"]
        }
    )
    assert response.status_code == 200
    assert "testing_strategies" in response.json()
    assert "testing_feedback" in response.json()

def test_propose_testing_strategy_endpoint_with_session(client):
    """Test que el endpoint mantiene el contexto de la sesión"""
    session_id = str(uuid4())
    response = client.post(
        "/api/v1/propose_testing_strategy",
        json={
            "session_id": session_id,
            "story": "Como usuario registrado quiero iniciar sesión con email y contraseña",
            "corner_cases": ["Usuario ingresa credenciales incorrectas"]
        }
    )
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id