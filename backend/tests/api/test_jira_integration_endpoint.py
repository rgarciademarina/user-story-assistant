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

def test_update_jira_story_create_new(client):
    """Test crear una nueva historia de usuario en Jira"""
    # Configurar variables de entorno para la prueba
    os.environ['JIRA_PROJECT_KEY'] = 'TESTPROJ'

    # Simular respuesta de creación de Jira
    mock_new_issue = {
        'key': 'TESTPROJ-123',
        'fields': {
            'summary': 'Nueva historia de prueba',
            'description': 'Descripción de prueba'
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.create_issue.return_value = mock_new_issue
        MockJira.return_value = mock_jira

        # Realizar solicitud de creación
        response = client.post("/api/v1/jira/story", json={
            "title": "Nueva historia de prueba",
            "description": "Descripción de prueba"
        })

        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data['story_id'] == 'TESTPROJ-123'
        assert data['action'] == 'created'
        assert 'creada exitosamente' in data['message']

def test_update_existing_jira_story(client):
    """Test actualizar una historia de usuario existente en Jira"""
    # Configurar variables de entorno para la prueba
    os.environ['JIRA_PROJECT_KEY'] = 'TESTPROJ'

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.update_issue.return_value = None
        MockJira.return_value = mock_jira

        # Realizar solicitud de actualización
        response = client.post("/api/v1/jira/story", json={
            "title": "Historia actualizada",
            "description": "Nueva descripción",
            "story_id": "TESTPROJ-456"
        })

        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data['story_id'] == 'TESTPROJ-456'
        assert data['action'] == 'updated'
        assert 'actualizada exitosamente' in data['message']

def test_update_jira_story_missing_configuration(client):
    """Test manejar la falta de configuración de Jira"""
    # Limpiar variables de entorno
    os.environ.pop('JIRA_URL', None)
    os.environ.pop('JIRA_TOKEN', None)
    os.environ.pop('JIRA_PROJECT_KEY', None)

    # Realizar solicitud
    response = client.post("/api/v1/jira/story", json={
        "title": "Historia sin configuración",
        "description": "Prueba de configuración incompleta"
    })

    # Verificar respuesta de error
    assert response.status_code == 500
    assert "Configuración incompleta" in response.json()['detail']

def test_update_jira_story_invalid_input(client):
    """Test validación de entrada para el endpoint"""
    # Realizar solicitud con título vacío
    response = client.post("/api/v1/jira/story", json={
        "title": "",
        "description": "Descripción de prueba"
    })

    # Verificar respuesta de error
    assert response.status_code == 422  # Unprocessable Entity

@pytest.fixture
def mock_jira_env():
    """Configurar variables de entorno para Jira"""
    original_env = {
        'JIRA_URL': os.getenv('JIRA_URL'),
        'JIRA_TOKEN': os.getenv('JIRA_TOKEN'),
        'JIRA_PROJECT_KEY': os.getenv('JIRA_PROJECT_KEY')
    }
    
    os.environ['JIRA_URL'] = 'http://test-jira.com'
    os.environ['JIRA_TOKEN'] = 'test-token'
    os.environ['JIRA_PROJECT_KEY'] = 'TESTPROJ'
    
    yield
    
    # Restaurar variables originales
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

def test_create_jira_story_success(mock_jira_env, client):
    """Probar creación exitosa de una nueva historia de Jira"""
    # Simular respuesta de creación de Jira
    mock_new_issue = {
        'key': 'TESTPROJ-123',
        'fields': {
            'summary': 'Nueva historia de prueba',
            'description': 'Descripción detallada'
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.create_issue.return_value = mock_new_issue
        MockJira.return_value = mock_jira

        # Realizar solicitud de creación
        response = client.post("/api/v1/jira/story", json={
            "title": "Nueva historia de prueba",
            "description": "Descripción detallada"
        })

        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data['story_id'] == 'TESTPROJ-123'
        assert data['action'] == 'created'
        assert 'creada exitosamente' in data['message']

def test_update_existing_jira_story_success(mock_jira_env, client):
    """Probar actualización exitosa de una historia de Jira existente"""
    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.update_issue_field.return_value = None
        MockJira.return_value = mock_jira

        # Realizar solicitud de actualización
        response = client.post("/api/v1/jira/story", json={
            "title": "Historia actualizada",
            "description": "Nueva descripción",
            "story_id": "TESTPROJ-456"
        })

        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data['story_id'] == 'TESTPROJ-456'
        assert data['action'] == 'updated'
        assert 'actualizada exitosamente' in data['message']

def test_create_jira_story_missing_configuration():
    """Probar manejo de error cuando faltan configuraciones de Jira"""
    # Limpiar variables de entorno
    os.environ.pop('JIRA_URL', None)
    os.environ.pop('JIRA_TOKEN', None)
    os.environ.pop('JIRA_PROJECT_KEY', None)

    client = TestClient(app)

    # Realizar solicitud
    response = client.post("/api/v1/jira/story", json={
        "title": "Historia sin configuración",
        "description": "Prueba de configuración incompleta"
    })

    # Verificar respuesta de error
    assert response.status_code == 500
    assert "Configuración incompleta" in response.json()['detail']

def test_create_jira_story_invalid_input():
    """Probar validación de entrada para el endpoint"""
    client = TestClient(app)

    # Casos de prueba con entradas inválidas
    invalid_inputs = [
        {"title": ""},  # Título vacío
        {"title": " " * 300},  # Título demasiado largo
    ]

    for invalid_input in invalid_inputs:
        response = client.post("/api/v1/jira/story", json=invalid_input)
        assert response.status_code == 422, f"Falló para entrada: {invalid_input}"

def test_update_jira_story_invalid_story_id(mock_jira_env, client):
    """Probar manejo de ID de historia inválido"""
    response = client.post("/api/v1/jira/story", json={
        "title": "Historia con ID inválido",
        "description": "Prueba de ID inválido",
        "story_id": "InvalidID"
    })

    assert response.status_code == 400
    assert "ID de historia inválido" in response.json()['detail']
