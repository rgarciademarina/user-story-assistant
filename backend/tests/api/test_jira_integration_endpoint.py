import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app
import os

@pytest.fixture
def client():
    # Configurar variables de entorno para el test
    os.environ['JIRA_URL'] = 'http://test-jira.com'
    os.environ['JIRA_TOKEN'] = 'test-token'
    return TestClient(app)

def test_get_jira_story_success(client):
    """Test que el endpoint devuelve correctamente una historia de Jira"""
    mock_issue = {
        'fields': {
            'summary': 'STORYASIS-1: Implementar login',
            'description': 'Como usuario quiero iniciar sesión'
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.return_value = mock_issue
        MockJira.return_value = mock_jira

        response = client.get("/api/v1/jira/story/STORYASIS-1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "STORYASIS-1: Implementar login"
        assert data["description"] == "Como usuario quiero iniciar sesión"

def test_get_jira_story_not_found(client):
    """Test que el endpoint maneja correctamente historias no encontradas"""
    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.side_effect = Exception("Issue Does Not Exist")
        MockJira.return_value = mock_jira

        response = client.get("/api/v1/jira/story/STORYASIS-999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Historia no encontrada"

def test_get_jira_story_server_error(client):
    """Test que el endpoint maneja correctamente errores del servidor de Jira"""
    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.side_effect = Exception("Error de conexión")
        MockJira.return_value = mock_jira

        response = client.get("/api/v1/jira/story/STORYASIS-1")
        
        assert response.status_code == 500
        assert "Error al conectar con Jira" in response.json()["detail"]

def test_get_jira_story_invalid_id(client):
    """Test que el endpoint valida correctamente el formato del ID"""
    response = client.get("/api/v1/jira/story/invalid-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "ID de historia inválido"
