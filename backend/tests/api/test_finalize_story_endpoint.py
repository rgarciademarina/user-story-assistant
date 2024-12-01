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

def test_finalize_story_endpoint_with_components_success(client):
    """Test que el endpoint de finalizar historia funciona correctamente con componentes individuales"""
    response = client.post(
        "/api/v1/finalize_story",
        json={
            "refined_story": "Como usuario registrado quiero iniciar sesión con email y contraseña",
            "corner_cases": [
                "Intentos de inicio de sesión con credenciales incorrectas",
                "Bloqueo de cuenta por múltiples intentos fallidos"
            ],
            "testing_strategy": [
                "Pruebas unitarias para validación de credenciales",
                "Pruebas de integración para el proceso de autenticación"
            ],
            "format_preferences": {
                "acceptance_criteria_format": "gherkin",
                "functional_tests_format": "gherkin"
            }
        }
    )
    assert response.status_code == 200
    assert "finalized_story" in response.json()
    assert "feedback" in response.json()
    assert isinstance(response.json()["session_id"], str)
    assert isinstance(response.json()["finalized_story"], str)

def test_finalize_story_endpoint_with_finalized_story_success(client):
    """Test que el endpoint maneja correctamente una historia finalizada con feedback"""
    response = client.post(
        "/api/v1/finalize_story",
        json={
            "finalized_story": """Historia Principal:
Como usuario registrado quiero iniciar sesión con email y contraseña

Criterios de Aceptación:
Given un usuario registrado
When intenta iniciar sesión con credenciales correctas
Then debe obtener acceso a su cuenta""",
            "feedback": "Añadir casos de autenticación de dos factores",
            "format_preferences": {
                "acceptance_criteria_format": "gherkin",
                "functional_tests_format": "gherkin"
            }
        }
    )
    assert response.status_code == 200
    assert "finalized_story" in response.json()
    assert "feedback" in response.json()
    assert isinstance(response.json()["session_id"], str)
    assert isinstance(response.json()["finalized_story"], str)

def test_finalize_story_endpoint_with_session(client):
    """Test que el endpoint mantiene el contexto de la sesión"""
    session_id = str(uuid4())
    response = client.post(
        "/api/v1/finalize_story",
        json={
            "session_id": session_id,
            "refined_story": "Como usuario registrado quiero iniciar sesión con email y contraseña",
            "corner_cases": ["Intentos de inicio de sesión con credenciales incorrectas"],
            "testing_strategy": ["Pruebas unitarias para validación de credenciales"]
        }
    )
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id

def test_finalize_story_endpoint_invalid_input(client):
    """Test que el endpoint maneja correctamente entradas inválidas"""
    response = client.post(
        "/api/v1/finalize_story",
        json={
            "refined_story": "Como usuario registrado quiero iniciar sesión con email y contraseña",
            "finalized_story": "Historia ya finalizada"  # No se pueden enviar ambos
        }
    )
    assert response.status_code == 422  # Error de validación

def test_finalize_story_endpoint_missing_components(client):
    """Test que el endpoint requiere todos los componentes cuando no se envía historia finalizada"""
    response = client.post(
        "/api/v1/finalize_story",
        json={
            "refined_story": "Como usuario registrado quiero iniciar sesión con email y contraseña"
            # Faltan corner_cases y testing_strategy
        }
    )
    assert response.status_code == 422  # Error de validación
